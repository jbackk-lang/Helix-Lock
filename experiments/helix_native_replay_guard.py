"""Opt-in replay detection for authenticated Helix envelopes.

SQLite uniqueness is atomic across cooperating processes. The database is a
security-critical state dependency: loss/rollback of it defeats replay defense.
This is a research receiver, not a network protocol or distributed consensus.
"""
from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import sqlite3

from experiments.helix_native_secure_envelope import recover_bytes


class ReplayDetected(ValueError):
    pass


class ReplayGuard:
    def __init__(self, database: str | Path):
        self.database = str(database)
        with sqlite3.connect(self.database, timeout=10) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS seen ("
                         "key_scope BLOB NOT NULL, envelope_id BLOB NOT NULL, "
                         "PRIMARY KEY (key_scope, envelope_id))")

    def recover_once(self, envelope: bytes, key: bytes) -> tuple[bytes, int]:
        # Authentication must happen before the envelope is admitted to state.
        result = recover_bytes(envelope, key)
        # Domain-separated keyed scope prevents cross-key collisions and avoids
        # writing raw keys to disk. Digest binds the exact authenticated bytes.
        scope = hmac.digest(key, b"helix-replay-scope-v1", "sha256")
        identifier = hashlib.sha256(envelope).digest()
        with sqlite3.connect(self.database, timeout=10) as conn:
            try:
                conn.execute("INSERT INTO seen (key_scope, envelope_id) VALUES (?, ?)",
                             (scope, identifier))
            except sqlite3.IntegrityError as exc:
                raise ReplayDetected("authenticated envelope already consumed") from exc
        return result
