import shutil
import sqlite3
import pytest

from experiments.helix_native_replay_guard import ReplayGuard
from experiments.helix_native_secure_envelope import generate_key, protect_bytes
from experiments.helix_replay_state_checkpoint import (
    StateIntegrityError, seal_state, verify_state,
)


def test_trusted_checkpoint_detects_rollback(tmp_path):
    db = tmp_path / "seen.sqlite"
    guard = ReplayGuard(db)
    key = generate_key()
    integrity_key = generate_key()
    previous = tmp_path / "previous.sqlite"
    shutil.copyfile(db, previous)
    guard.recover_once(protect_bytes(b"first", key), key)
    checkpoint = seal_state(db, integrity_key)
    verify_state(db, integrity_key, checkpoint)
    shutil.copyfile(previous, db)
    with pytest.raises(StateIntegrityError):
        verify_state(db, integrity_key, checkpoint)


def test_trusted_checkpoint_detects_row_deletion(tmp_path):
    db = tmp_path / "seen.sqlite"
    guard = ReplayGuard(db)
    key = generate_key()
    guard.recover_once(protect_bytes(b"first", key), key)
    checkpoint = seal_state(db, generate_key())
    with sqlite3.connect(db) as conn:
        conn.execute("DELETE FROM seen")
    with pytest.raises(StateIntegrityError):
        verify_state(db, generate_key(), checkpoint)


def test_invalid_key_and_checkpoint(tmp_path):
    db = tmp_path / "seen.sqlite"
    ReplayGuard(db)
    with pytest.raises(ValueError):
        seal_state(db, b"short")
    with pytest.raises(StateIntegrityError):
        verify_state(db, generate_key(), b"short")
