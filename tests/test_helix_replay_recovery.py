import sqlite3

import pytest

from experiments.helix_native_replay_guard import ReplayGuard
from experiments.helix_native_secure_envelope import generate_key, protect_bytes
from experiments.helix_replay_state_checkpoint import seal_state
from experiments.helix_replay_recovery import (
    RecoveryRequired, inspect_replay_state, verify_before_resume,
)


def test_consistent_state_can_resume(tmp_path):
    db = tmp_path / "seen.sqlite"
    ReplayGuard(db)
    key = generate_key()
    checkpoint = seal_state(db, key)
    assert inspect_replay_state(db, key, checkpoint) == "consistent"
    verify_before_resume(db, key, lambda: checkpoint)


def test_external_advance_without_local_commit_requires_recovery(tmp_path):
    db = tmp_path / "seen.sqlite"
    ReplayGuard(db)
    key = generate_key()
    with pytest.raises(RecoveryRequired):
        inspect_replay_state(db, key, b"x" * 32)


def test_rollback_or_deleted_rows_cannot_resume(tmp_path):
    db = tmp_path / "seen.sqlite"
    guard = ReplayGuard(db)
    key = generate_key()
    guard.recover_once(protect_bytes(b"accepted", key), key)
    checkpoint = seal_state(db, key)
    with sqlite3.connect(db) as conn:
        conn.execute("DELETE FROM seen")
    with pytest.raises(RecoveryRequired):
        verify_before_resume(db, key, lambda: checkpoint)


def test_missing_or_unavailable_trust_fails_closed(tmp_path):
    db = tmp_path / "seen.sqlite"
    ReplayGuard(db)
    key = generate_key()
    with pytest.raises(RecoveryRequired):
        inspect_replay_state(db, key, b"")
    with pytest.raises(RecoveryRequired):
        verify_before_resume(db, key, lambda: (_ for _ in ()).throw(OSError("offline")))
