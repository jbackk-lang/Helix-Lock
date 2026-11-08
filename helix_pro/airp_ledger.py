"""Hash-chained AIRP audit ledger with signed, externally anchored checkpoints.

The SQLite ledger is tamper-evident, not independently rollback-resistant.
Rollback resistance exists only when a separately administered TrustAnchor
retains checkpoints and enforces monotonic sequence/head-hash updates.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .cipher import HelixProError

GENESIS_HASH = "0" * 64
MAX_PAYLOAD_BYTES = 16_384


class TrustAnchor(Protocol):
    """Independent service contract.

    publish_checkpoint must atomically reject lower sequence numbers and
    same-sequence/different-hash forks. latest_checkpoint returns the exact
    canonical checkpoint bytes previously accepted, or None.
    """

    def publish_checkpoint(self, checkpoint: bytes) -> None: ...
    def latest_checkpoint(self) -> bytes | None: ...


@dataclass(frozen=True)
class LedgerVerification:
    valid: bool
    status: str
    local_sequence: int
    anchored_sequence: int
    head_hash: str


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _event_hash(event: dict) -> str:
    return hashlib.sha256(_canonical(event)).hexdigest()


class AIRPIntegrityLedger:
    """Append-only event chain and Ed25519 checkpoints for AIRP.

    Never put plaintext, data keys, passwords, recovery keys, or bearer tokens
    in event payloads. Store only identifiers, hashes, counters and decisions.
    """

    def __init__(
        self,
        database_path: str | Path,
        signing_key: Ed25519PrivateKey,
        *,
        trust_anchor: TrustAnchor | None = None,
        trusted_public_key: bytes | None = None,
    ):
        if not isinstance(signing_key, Ed25519PrivateKey):
            raise HelixProError("signing_key must be an Ed25519PrivateKey")
        self.database_path = str(database_path)
        if self.database_path == ":memory:":
            raise HelixProError("AIRPIntegrityLedger requires a persistent SQLite file")
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._signing_key = signing_key
        self._public_key = signing_key.public_key()
        self._trusted_public_key = (
            Ed25519PublicKey.from_public_bytes(trusted_public_key)
            if trusted_public_key is not None else self._public_key
        )
        self._anchor = trust_anchor
        with closing(self._connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("""
                CREATE TABLE IF NOT EXISTS airp_ledger_events (
                    sequence INTEGER PRIMARY KEY CHECK(sequence >= 1),
                    timestamp_utc TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    object_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS airp_ledger_object_sequence ON airp_ledger_events(object_id, sequence)")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database_path, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=15000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    @property
    def public_key_bytes(self) -> bytes:
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def _append_locked(self, db: sqlite3.Connection, event_type: str, object_id: str, payload: dict) -> dict:
        row = db.execute(
            "SELECT sequence,event_hash FROM airp_ledger_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        sequence = 1 if row is None else row["sequence"] + 1
        previous_hash = GENESIS_HASH if row is None else row["event_hash"]
        timestamp = datetime.now(timezone.utc).isoformat()
        payload_json = _canonical(payload).decode("utf-8")
        event = {
            "sequence": sequence,
            "timestamp_utc": timestamp,
            "event_type": event_type,
            "object_id": object_id,
            "payload": payload,
            "previous_hash": previous_hash,
        }
        digest = _event_hash(event)
        db.execute(
            "INSERT INTO airp_ledger_events VALUES (?,?,?,?,?,?,?)",
            (sequence, timestamp, event_type, object_id, payload_json, previous_hash, digest),
        )
        return {**event, "event_hash": digest}

    def append(self, event_type: str, object_id: str, payload: dict | None = None) -> dict:
        if not isinstance(event_type, str) or not event_type or len(event_type) > 80:
            raise HelixProError("event_type must contain 1..80 characters")
        if not isinstance(object_id, str) or not object_id or len(object_id) > 512:
            raise HelixProError("object_id must contain 1..512 characters")
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            raise HelixProError("ledger payload must be a JSON object")
        try:
            encoded = _canonical(payload)
        except (TypeError, ValueError) as exc:
            raise HelixProError("ledger payload must contain JSON-compatible values") from exc
        if len(encoded) > MAX_PAYLOAD_BYTES:
            raise HelixProError("ledger payload exceeds 16 KiB")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                event = self._append_locked(db, event_type, object_id, payload)
                db.execute("COMMIT")
                return event
            except Exception:
                db.execute("ROLLBACK")
                raise

    def observe_counter(self, object_id: str, counter: int, blob_sha256: str) -> dict:
        """Atomically reject repeated/decreasing CounterLock counters per object."""
        if not isinstance(counter, int) or isinstance(counter, bool) or counter < 0 or counter > (2**64 - 1):
            raise HelixProError("counter must be an unsigned 64-bit integer")
        if not isinstance(blob_sha256, str) or len(blob_sha256) != 64:
            raise HelixProError("blob_sha256 must be a SHA-256 hex digest")
        try:
            int(blob_sha256, 16)
        except ValueError as exc:
            raise HelixProError("blob_sha256 must be a SHA-256 hex digest") from exc
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute(
                    "SELECT payload_json FROM airp_ledger_events "
                    "WHERE object_id=? AND event_type='counter_observed' "
                    "ORDER BY sequence DESC LIMIT 1", (object_id,)
                ).fetchone()
                if row is not None:
                    previous = json.loads(row["payload_json"])["counter"]
                    if counter <= previous:
                        raise HelixProError("CounterLock replay or rollback detected")
                event = self._append_locked(
                    db, "counter_observed", object_id,
                    {"counter": counter, "blob_sha256": blob_sha256.lower()},
                )
                db.execute("COMMIT")
                return event
            except Exception:
                db.execute("ROLLBACK")
                raise

    def events(self, object_id: str | None = None) -> tuple[dict, ...]:
        with closing(self._connect()) as db:
            if object_id is None:
                rows = db.execute("SELECT * FROM airp_ledger_events ORDER BY sequence").fetchall()
            else:
                rows = db.execute("SELECT * FROM airp_ledger_events WHERE object_id=? ORDER BY sequence", (object_id,)).fetchall()
        return tuple({
            "sequence": row["sequence"],
            "timestamp_utc": row["timestamp_utc"],
            "event_type": row["event_type"],
            "object_id": row["object_id"],
            "payload": json.loads(row["payload_json"]),
            "previous_hash": row["previous_hash"],
            "event_hash": row["event_hash"],
        } for row in rows)

    def head(self) -> tuple[int, str]:
        with closing(self._connect()) as db:
            row = db.execute("SELECT sequence,event_hash FROM airp_ledger_events ORDER BY sequence DESC LIMIT 1").fetchone()
        return (0, GENESIS_HASH) if row is None else (row["sequence"], row["event_hash"])

    def verify_chain(self) -> bool:
        expected_sequence = 1
        previous_hash = GENESIS_HASH
        for event in self.events():
            material = {
                "sequence": event["sequence"],
                "timestamp_utc": event["timestamp_utc"],
                "event_type": event["event_type"],
                "object_id": event["object_id"],
                "payload": event["payload"],
                "previous_hash": event["previous_hash"],
            }
            if event["sequence"] != expected_sequence or event["previous_hash"] != previous_hash:
                return False
            if _event_hash(material) != event["event_hash"]:
                return False
            expected_sequence += 1
            previous_hash = event["event_hash"]
        return True

    def create_checkpoint(self) -> bytes:
        sequence, head_hash = self.head()
        unsigned = {
            "schema": 1,
            "sequence": sequence,
            "head_hash": head_hash,
            "public_key": self.public_key_bytes.hex(),
        }
        signature = self._signing_key.sign(_canonical(unsigned))
        return _canonical({**unsigned, "signature": signature.hex()})

    @staticmethod
    def verify_checkpoint(checkpoint: bytes, trusted_public_key: bytes) -> dict:
        try:
            parsed = json.loads(checkpoint.decode("utf-8"))
            required = {"schema", "sequence", "head_hash", "public_key", "signature"}
            if not isinstance(parsed, dict) or set(parsed) != required or parsed["schema"] != 1:
                raise ValueError("invalid checkpoint schema")
            if parsed["public_key"] != trusted_public_key.hex():
                raise ValueError("checkpoint signer does not match pinned public key")
            unsigned = {key: parsed[key] for key in ("schema", "sequence", "head_hash", "public_key")}
            Ed25519PublicKey.from_public_bytes(trusted_public_key).verify(
                bytes.fromhex(parsed["signature"]), _canonical(unsigned)
            )
            if type(parsed["sequence"]) is not int or parsed["sequence"] < 0:
                raise ValueError("invalid checkpoint sequence")
            if not isinstance(parsed["head_hash"], str) or len(parsed["head_hash"]) != 64:
                raise ValueError("invalid checkpoint head hash")
            int(parsed["head_hash"], 16)
            return parsed
        except Exception as exc:
            raise HelixProError(f"invalid AIRP checkpoint: {exc}") from exc

    def publish_checkpoint(self) -> bytes:
        if self._anchor is None:
            raise HelixProError("no independent AIRP trust anchor is configured")
        if not self.verify_chain():
            raise HelixProError("local AIRP hash chain is invalid; checkpoint not published")
        checkpoint = self.create_checkpoint()
        self._anchor.publish_checkpoint(checkpoint)
        return checkpoint

    def verify(self) -> LedgerVerification:
        local_sequence, local_hash = self.head()
        if not self.verify_chain():
            return LedgerVerification(False, "local_chain_invalid", local_sequence, 0, local_hash)
        if self._anchor is None:
            return LedgerVerification(True, "local_only_unanchored", local_sequence, 0, local_hash)
        remote_bytes = self._anchor.latest_checkpoint()
        if remote_bytes is None:
            return LedgerVerification(True, "anchor_empty_unanchored", local_sequence, 0, local_hash)
        try:
            remote = self.verify_checkpoint(remote_bytes, self._trusted_public_key.public_bytes(
                encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
            ))
        except HelixProError:
            return LedgerVerification(False, "anchor_signature_invalid", local_sequence, 0, local_hash)
        anchored_sequence = remote["sequence"]
        if anchored_sequence > local_sequence:
            return LedgerVerification(False, "local_rollback_detected", local_sequence, anchored_sequence, local_hash)
        if anchored_sequence == 0:
            anchored_hash = GENESIS_HASH
        else:
            events = self.events()
            if anchored_sequence > len(events):
                return LedgerVerification(False, "anchored_prefix_missing", local_sequence, anchored_sequence, local_hash)
            anchored_hash = events[anchored_sequence - 1]["event_hash"]
        if anchored_hash != remote["head_hash"]:
            return LedgerVerification(False, "anchored_history_fork_or_tampering", local_sequence, anchored_sequence, local_hash)
        if local_sequence > anchored_sequence:
            return LedgerVerification(True, "valid_with_unanchored_suffix", local_sequence, anchored_sequence, local_hash)
        return LedgerVerification(True, "fully_anchored", local_sequence, anchored_sequence, local_hash)
