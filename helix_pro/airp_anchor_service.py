"""Reference HTTP service for independently administered AIRP checkpoints.

Run behind a TLS reverse proxy for remote use. The process stores only signed
checkpoint metadata, never plaintext or encryption/recovery keys.
"""
from __future__ import annotations

import hmac
import json
import os
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from cryptography.hazmat.primitives import serialization

from .airp_ledger import AIRPIntegrityLedger
from .cipher import HelixProError

MAX_CHECKPOINT_BYTES = 8192


class AnchorRepository:
    """SQLite-backed monotonic checkpoint register."""

    def __init__(self, database_path: str | Path, trusted_public_key: bytes):
        if len(trusted_public_key) != 32:
            raise HelixProError("trusted Ed25519 public key must be 32 bytes")
        self.database_path = str(database_path)
        self.trusted_public_key = bytes(trusted_public_key)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("""
                CREATE TABLE IF NOT EXISTS airp_trust_checkpoints (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    sequence INTEGER NOT NULL,
                    head_hash TEXT NOT NULL,
                    checkpoint BLOB NOT NULL,
                    updated_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _connect(self):
        db = sqlite3.connect(self.database_path, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=15000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def publish(self, checkpoint: bytes) -> dict:
        if not isinstance(checkpoint, bytes) or not checkpoint or len(checkpoint) > MAX_CHECKPOINT_BYTES:
            raise HelixProError("checkpoint must be 1..8192 bytes")
        parsed = AIRPIntegrityLedger.verify_checkpoint(checkpoint, self.trusted_public_key)
        sequence, head_hash = parsed["sequence"], parsed["head_hash"]
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                current = db.execute(
                    "SELECT sequence,head_hash,checkpoint FROM airp_trust_checkpoints WHERE singleton=1"
                ).fetchone()
                if current is not None:
                    if sequence < current["sequence"]:
                        raise HelixProError("checkpoint rollback rejected")
                    if sequence == current["sequence"]:
                        if head_hash != current["head_hash"]:
                            raise HelixProError("checkpoint fork rejected at an existing sequence")
                        db.execute("COMMIT")
                        return {"accepted": True, "idempotent": True, "sequence": sequence, "head_hash": head_hash}
                db.execute("""
                    INSERT INTO airp_trust_checkpoints(singleton,sequence,head_hash,checkpoint)
                    VALUES(1,?,?,?)
                    ON CONFLICT(singleton) DO UPDATE SET
                        sequence=excluded.sequence,
                        head_hash=excluded.head_hash,
                        checkpoint=excluded.checkpoint,
                        updated_utc=CURRENT_TIMESTAMP
                """, (sequence, head_hash, checkpoint))
                db.execute("COMMIT")
                return {"accepted": True, "idempotent": False, "sequence": sequence, "head_hash": head_hash}
            except Exception:
                db.execute("ROLLBACK")
                raise

    def latest(self) -> bytes | None:
        with closing(self._connect()) as db:
            row = db.execute(
                "SELECT checkpoint FROM airp_trust_checkpoints WHERE singleton=1"
            ).fetchone()
        return None if row is None else bytes(row["checkpoint"])


def make_handler(repository: AnchorRepository, bearer_token: str):
    if not bearer_token or len(bearer_token) < 32:
        raise HelixProError("AIRP_ANCHOR_TOKEN must contain at least 32 characters")

    class Handler(BaseHTTPRequestHandler):
        server_version = "AIRP-TrustAnchor/1"

        def log_message(self, fmt, *args):
            # Avoid logging authorization headers, request bodies or secrets.
            super().log_message(fmt, *args)

        def _json(self, status: int, payload: dict):
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authorized(self) -> bool:
            supplied = self.headers.get("Authorization", "")
            expected = "Bearer " + bearer_token
            return hmac.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8"))

        def do_GET(self):
            if self.path != "/v1/checkpoints/latest":
                self._json(404, {"error": "not_found"})
                return
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            checkpoint = repository.latest()
            if checkpoint is None:
                self._json(404, {"error": "no_checkpoint"})
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(checkpoint)))
            self.end_headers()
            self.wfile.write(checkpoint)

        def do_POST(self):
            if self.path != "/v1/checkpoints":
                self._json(404, {"error": "not_found"})
                return
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._json(400, {"error": "invalid_content_length"})
                return
            if length < 1 or length > MAX_CHECKPOINT_BYTES:
                self._json(413, {"error": "invalid_checkpoint_size"})
                return
            try:
                result = repository.publish(self.rfile.read(length))
                self._json(200, result)
            except (HelixProError, ValueError, UnicodeError) as exc:
                self._json(409, {"error": "checkpoint_rejected", "detail": str(exc)[:200]})

    return Handler


def serve(
    database_path: str,
    trusted_public_key_hex: str,
    bearer_token: str,
    *,
    host: str = "127.0.0.1",
    port: int = 8790,
):
    """Start the service. Remote deployments must terminate TLS at a trusted proxy."""
    try:
        public_key = bytes.fromhex(trusted_public_key_hex)
    except ValueError as exc:
        raise HelixProError("AIRP_ANCHOR_PUBLIC_KEY_HEX is not valid hex") from exc
    repository = AnchorRepository(database_path, public_key)
    server = ThreadingHTTPServer((host, port), make_handler(repository, bearer_token))
    print(f"AIRP Trust Anchor listening on http://{host}:{port} (TLS required for remote access)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    serve(
        os.environ.get("AIRP_ANCHOR_DB", "private_state/airp-anchor.sqlite3"),
        os.environ["AIRP_ANCHOR_PUBLIC_KEY_HEX"],
        os.environ["AIRP_ANCHOR_TOKEN"],
        host=os.environ.get("AIRP_ANCHOR_HOST", "127.0.0.1"),
        port=int(os.environ.get("AIRP_ANCHOR_PORT", "8790")),
    )
