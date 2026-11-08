import sqlite3
import pytest

from experiments.helix_native_replay_guard import ReplayDetected, ReplayGuard
from experiments.helix_native_secure_envelope import generate_key, protect_bytes
from experiments.helix_replay_state_checkpoint import seal_state, StateIntegrityError
from experiments.helix_guarded_replay_receiver import GuardedReplayReceiver


class Trust:
    def __init__(self, value):
        self.value = value
        self.fail = False

    def read(self):
        return self.value

    def advance(self, old, new):
        if self.fail:
            raise OSError("external checkpoint unavailable")
        if self.value != old:
            raise StateIntegrityError("stale checkpoint")
        self.value = new


def receiver(tmp_path):
    db = tmp_path / "state.sqlite"
    ReplayGuard(db)
    key = generate_key()
    trust = Trust(seal_state(db, key))
    return GuardedReplayReceiver(db, key, trust.read, trust.advance), trust


def test_authenticated_replay_is_rejected(tmp_path):
    guard, _ = receiver(tmp_path)
    key = generate_key()
    msg = protect_bytes(b"one-time", key)
    assert guard.recover_once(msg, key)[0] == b"one-time"
    with pytest.raises(ReplayDetected):
        guard.recover_once(msg, key)


def test_checkpoint_failure_rolls_back_db(tmp_path):
    guard, trust = receiver(tmp_path)
    key = generate_key()
    msg = protect_bytes(b"once", key)
    trust.fail = True
    with pytest.raises(OSError):
        guard.recover_once(msg, key)
    with sqlite3.connect(guard.database) as conn:
        assert conn.execute("SELECT count(*) FROM seen").fetchone()[0] == 0
    trust.fail = False
    assert guard.recover_once(msg, key)[0] == b"once"


def test_rollback_detected_and_fail_closed(tmp_path):
    guard, trust = receiver(tmp_path)
    key = generate_key()
    msg = protect_bytes(b"once", key)
    guard.recover_once(msg, key)
    with sqlite3.connect(guard.database) as conn:
        conn.execute("DELETE FROM seen")
    with pytest.raises(StateIntegrityError):
        guard.recover_once(msg, key)
