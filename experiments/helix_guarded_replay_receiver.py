"""Fail-closed, transactional replay admission with an external checkpoint callback.

The callback MUST atomically persist the new checkpoint in an independent
non-rollbackable trust domain, and MUST NOT return success prematurely.
SQLite and an external store cannot share an ACID transaction here: a crash
between external checkpoint and SQLite commit causes a safe lockout, not an
undetected replay. Recovery requires trusted operator reconciliation.
This is a research prototype; no production-ready hardware trust backend.
"""
from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import sqlite3
import struct
from typing import Callable

from experiments.helix_native_secure_envelope import recover_bytes
from experiments.helix_native_replay_guard import ReplayDetected
from experiments.helix_replay_state_checkpoint import StateIntegrityError


def _digest_rows(conn: sqlite3.Connection) -> bytes:
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


def _seal(conn: sqlite3.Connection, key: bytes) -> bytes:
    return hmac.digest(key, b"helix-replay-checkpoint-v1" + _digest_rows(conn), "sha256")


class GuardedReplayReceiver:
    def __init__(self, database: str | Path, integrity_key: bytes,
                 read_checkpoint: Callable[[], bytes],
                 advance_checkpoint: Callable[[bytes, bytes], None]):
        if len(integrity_key) < 32:
            raise ValueError("integrity key must contain at least 32 bytes")
        self.database = str(database)
        self.integrity_key = integrity_key
        self.read_checkpoint = read_checkpoint
        self.advance_checkpoint = advance_checkpoint

    def recover_once(self, envelope: bytes, key: bytes) -> tuple[bytes, int]:
        result = recover_bytes(envelope, key)
        scope = hmac.digest(key, b"helix-replay-scope-v1", "sha256")
        identifier = hashlib.sha256(envelope).digest()
        with sqlite3.connect(self.database, timeout=10, isolation_level=None) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                before = _seal(conn, self.integrity_key)
                checkpoint = self.read_checkpoint()
                if not hmac.compare_digest(before, checkpoint):
                    raise StateIntegrityError("trusted checkpoint mismatch; fail closed")
                try:
                    conn.execute("INSERT INTO seen VALUES (?, ?)", (scope, identifier))
                except sqlite3.IntegrityError as exc:
                    raise ReplayDetected("authenticated envelope already consumed") from exc
                after = _seal(conn, self.integrity_key)
                # Advance external trust FIRST. If SQLite commit fails, next
                # attempt sees mismatch and locks out instead of replaying.
                self.advance_checkpoint(before, after)
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
        return result
