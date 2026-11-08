"""HMAC-sealed replay-state checkpoint for the opt-in SQLite replay guard.

This detects modification and rollback only when the expected checkpoint is
stored in a separate trusted, non-rollbackable location. A checkpoint saved
beside the database is NOT rollback protection. Do not expose the HMAC key.
"""
from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import sqlite3
import struct


class StateIntegrityError(ValueError):
    pass


def state_digest(database: str | Path) -> bytes:
    """Canonical sorted rows; avoids dependence on SQLite file layout."""
    with sqlite3.connect(str(database), timeout=10) as conn:
        rows = conn.execute(
            "SELECT key_scope, envelope_id FROM seen ORDER BY key_scope, envelope_id"
        ).fetchall()
    digest = hashlib.sha256(b"helix-replay-state-v1")
    digest.update(struct.pack(">Q", len(rows)))
    for scope, identifier in rows:
        digest.update(struct.pack(">I", len(scope)))
        digest.update(scope)
        digest.update(struct.pack(">I", len(identifier)))
        digest.update(identifier)
    return digest.digest()


def seal_state(database: str | Path, integrity_key: bytes) -> bytes:
    if len(integrity_key) < 32:
        raise ValueError("integrity key must contain at least 32 bytes")
    return hmac.digest(integrity_key, b"helix-replay-checkpoint-v1" + state_digest(database),
                       "sha256")


def verify_state(database: str | Path, integrity_key: bytes, trusted_checkpoint: bytes) -> None:
    if len(trusted_checkpoint) != 32:
        raise StateIntegrityError("invalid checkpoint length")
    expected = seal_state(database, integrity_key)
    if not hmac.compare_digest(expected, trusted_checkpoint):
        raise StateIntegrityError("replay state differs from trusted checkpoint")
