"""Durable SQLite metadata store for AIRP object versions and access events.

Security boundary: SQLite durability is not rollback resistance against an
attacker who can replace both the encrypted object and this database/backups.
For that threat model, place the state in an independently administered,
append-only/transactional service. This module never stores keys or plaintext.
"""
from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .cipher import HelixProError


@dataclass(frozen=True)
class StoredRepresentation:
    object_id: str
    version: int
    key_id: str
    blob_sha256: str
    updated_utc: str


class AIRPStore:
    """SQLite-backed version registry with compare-and-swap rotation commits."""

    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        if self.database_path == ":memory:":
            raise HelixProError("AIRPStore requires a persistent SQLite file path")
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS airp_objects (
                    object_id TEXT PRIMARY KEY,
                    version INTEGER NOT NULL CHECK(version >= 1),
                    key_id TEXT NOT NULL,
                    blob_sha256 TEXT NOT NULL,
                    updated_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS airp_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_id TEXT NOT NULL,
                    timestamp_utc TEXT NOT NULL,
                    outcome TEXT NOT NULL CHECK(outcome IN ('granted','denied','rotated','rejected')),
                    version INTEGER NOT NULL,
                    key_id TEXT NOT NULL,
                    blob_sha256 TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS airp_events_object_id
                    ON airp_events(object_id, event_id);
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database_path, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def fingerprint(blob: bytes) -> str:
        return hashlib.sha256(blob).hexdigest()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _row(row: sqlite3.Row | None) -> StoredRepresentation | None:
        if row is None:
            return None
        return StoredRepresentation(
            object_id=row["object_id"], version=row["version"],
            key_id=row["key_id"], blob_sha256=row["blob_sha256"],
            updated_utc=row["updated_utc"],
        )

    def register(self, object_id: str, blob: bytes, *, key_id: str) -> StoredRepresentation:
        if not object_id or not key_id:
            raise HelixProError("object_id and key_id must be non-empty")
        now = self._now()
        digest = self.fingerprint(blob)
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute(
                    "INSERT INTO airp_objects VALUES (?,1,?,?,?)",
                    (object_id, key_id, digest, now),
                )
                db.execute(
                    "INSERT INTO airp_events(object_id,timestamp_utc,outcome,version,key_id,blob_sha256,detail) VALUES (?,?,?,?,?,?,?)",
                    (object_id, now, "granted", 1, key_id, digest, "registered"),
                )
                row = db.execute("SELECT * FROM airp_objects WHERE object_id=?", (object_id,)).fetchone()
                db.execute("COMMIT")
                return self._row(row)  # type: ignore[return-value]
            except Exception:
                db.execute("ROLLBACK")
                raise

    def get(self, object_id: str) -> StoredRepresentation | None:
        with closing(self._connect()) as db:
            return self._row(db.execute(
                "SELECT * FROM airp_objects WHERE object_id=?", (object_id,)
            ).fetchone())

    def verify(self, object_id: str, blob: bytes, *, version: int, key_id: str) -> bool:
        state = self.get(object_id)
        valid = bool(
            state and state.version == version and state.key_id == key_id
            and state.blob_sha256 == self.fingerprint(blob)
        )
        self.record_event(
            object_id, outcome="granted" if valid else "denied",
            detail="representation verified" if valid else "version/key/hash mismatch",
        )
        return valid

    def record_event(self, object_id: str, *, outcome: str, detail: str = "") -> None:
        if outcome not in {"granted", "denied", "rotated", "rejected"}:
            raise HelixProError("unsupported AIRP event outcome")
        if len(detail) > 240:
            raise HelixProError("event detail too long")
        now = self._now()
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute("SELECT * FROM airp_objects WHERE object_id=?", (object_id,)).fetchone()
                if row is None:
                    raise HelixProError("unknown AIRP object_id")
                db.execute(
                    "INSERT INTO airp_events(object_id,timestamp_utc,outcome,version,key_id,blob_sha256,detail) VALUES (?,?,?,?,?,?,?)",
                    (object_id, now, outcome, row["version"], row["key_id"], row["blob_sha256"], detail),
                )
                db.execute("COMMIT")
            except Exception:
                db.execute("ROLLBACK")
                raise

    def commit_rotation(
        self, object_id: str, new_blob: bytes, *, expected_version: int,
        expected_blob_sha256: str, new_key_id: str,
    ) -> StoredRepresentation:
        """Atomically advance metadata if the prior version still matches.

        Caller must first create and verify new_blob via rotate_encrypted_blob
        or rotate_counter_blob, then persist the blob safely. This transaction
        prevents concurrent stale writers but cannot atomically commit an
        external file and this DB together; use staged files/recovery on crash.
        """
        if not new_key_id:
            raise HelixProError("new_key_id must be non-empty")
        now = self._now()
        digest = self.fingerprint(new_blob)
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute("SELECT * FROM airp_objects WHERE object_id=?", (object_id,)).fetchone()
                if row is None:
                    raise HelixProError("unknown AIRP object_id")
                if row["version"] != expected_version or row["blob_sha256"] != expected_blob_sha256:
                    raise HelixProError("stale AIRP state; rotation rejected")
                if row["key_id"] == new_key_id:
                    raise HelixProError("new_key_id must differ from current key_id")
                next_version = expected_version + 1
                db.execute(
                    "UPDATE airp_objects SET version=?,key_id=?,blob_sha256=?,updated_utc=? WHERE object_id=?",
                    (next_version, new_key_id, digest, now, object_id),
                )
                db.execute(
                    "INSERT INTO airp_events(object_id,timestamp_utc,outcome,version,key_id,blob_sha256,detail) VALUES (?,?,?,?,?,?,?)",
                    (object_id, now, "rotated", next_version, new_key_id, digest, "key rotation committed"),
                )
                updated = db.execute("SELECT * FROM airp_objects WHERE object_id=?", (object_id,)).fetchone()
                db.execute("COMMIT")
                return self._row(updated)  # type: ignore[return-value]
            except Exception:
                db.execute("ROLLBACK")
                raise

    def events(self, object_id: str) -> tuple[dict, ...]:
        with closing(self._connect()) as db:
            rows = db.execute(
                "SELECT event_id,object_id,timestamp_utc,outcome,version,key_id,blob_sha256,detail "
                "FROM airp_events WHERE object_id=? ORDER BY event_id", (object_id,)
            ).fetchall()
            return tuple(dict(row) for row in rows)
