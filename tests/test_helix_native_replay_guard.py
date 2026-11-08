import sqlite3
import pytest
from cryptography.exceptions import InvalidTag

from experiments.helix_native_replay_guard import ReplayDetected, ReplayGuard
from experiments.helix_native_secure_envelope import generate_key, protect_bytes


def test_replay_rejected_across_restarts(tmp_path):
    db = tmp_path / "seen.sqlite"
    key = generate_key()
    envelope = protect_bytes(b"important", key)
    assert ReplayGuard(db).recover_once(envelope, key)[0] == b"important"
    with pytest.raises(ReplayDetected):
        ReplayGuard(db).recover_once(envelope, key)
    assert ReplayGuard(db).recover_once(protect_bytes(b"important", key), key)[0] == b"important"


def test_invalid_envelope_does_not_consume_replay_slot(tmp_path):
    guard = ReplayGuard(tmp_path / "seen.sqlite")
    key = generate_key()
    envelope = protect_bytes(b"valid", key)
    corrupted = bytearray(envelope)
    corrupted[-1] ^= 1
    with pytest.raises(InvalidTag):
        guard.recover_once(bytes(corrupted), key)
    assert guard.recover_once(envelope, key)[0] == b"valid"


def test_database_is_security_state(tmp_path):
    db = tmp_path / "seen.sqlite"
    guard = ReplayGuard(db)
    key = generate_key()
    envelope = protect_bytes(b"valid", key)
    guard.recover_once(envelope, key)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT count(*) FROM seen").fetchone()[0] == 1
