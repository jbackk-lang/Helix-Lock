"""Adversarial tests for fail-closed guarded replay admission.

The trust implementation here is a synchronized test double, NOT a secure
non-rollbackable hardware or remote trust backend.
"""
from concurrent.futures import ThreadPoolExecutor
import threading
import sqlite3

import pytest

from experiments.helix_guarded_replay_receiver import GuardedReplayReceiver
from experiments.helix_native_replay_guard import ReplayDetected, ReplayGuard
from experiments.helix_native_secure_envelope import generate_key, protect_bytes
from experiments.helix_replay_state_checkpoint import seal_state, StateIntegrityError


class AtomicTrust:
    def __init__(self, checkpoint):
        self._checkpoint = checkpoint
        self._lock = threading.Lock()
        self.updates = 0
        self.unavailable = False

    def read(self):
        with self._lock:
            return self._checkpoint

    def advance(self, expected, next_value):
        with self._lock:
            if self.unavailable:
                raise ConnectionError("checkpoint unavailable")
            if self._checkpoint != expected:
                raise StateIntegrityError("stale external checkpoint")
            self._checkpoint = next_value
            self.updates += 1


def setup(tmp_path):
    db = tmp_path / "replay.sqlite"
    ReplayGuard(db)
    integrity_key = generate_key()
    trust = AtomicTrust(seal_state(db, integrity_key))
    guard = GuardedReplayReceiver(db, integrity_key, trust.read, trust.advance)
    return guard, trust


def test_concurrent_replay_exactly_one_accepted(tmp_path):
    guard, trust = setup(tmp_path)
    key = generate_key()
    envelope = protect_bytes(b"single authorization", key)

    def attempt(_):
        try:
            guard.recover_once(envelope, key)
            return "accepted"
        except ReplayDetected:
            return "replay"

    with ThreadPoolExecutor(max_workers=12) as pool:
        outcomes = list(pool.map(attempt, range(40)))
    assert outcomes.count("accepted") == 1
    assert outcomes.count("replay") == 39
    assert trust.updates == 1


def test_distinct_concurrent_messages_and_checkpoint(tmp_path):
    guard, trust = setup(tmp_path)
    key = generate_key()
    messages = [protect_bytes(i.to_bytes(4, "big"), key) for i in range(24)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        outputs = list(pool.map(lambda msg: guard.recover_once(msg, key)[0], messages))
    assert outputs == [i.to_bytes(4, "big") for i in range(24)]
    assert trust.updates == 24
    assert trust.read() == seal_state(guard.database, guard.integrity_key)


def test_checkpoint_unavailable_fails_closed_without_consuming(tmp_path):
    guard, trust = setup(tmp_path)
    key = generate_key()
    message = protect_bytes(b"valid", key)
    trust.unavailable = True
    with pytest.raises(ConnectionError):
        guard.recover_once(message, key)
    with sqlite3.connect(guard.database) as conn:
        assert conn.execute("SELECT count(*) FROM seen").fetchone()[0] == 0
    trust.unavailable = False
    assert guard.recover_once(message, key)[0] == b"valid"


def test_trust_advanced_but_sqlite_not_committed_locks_out(tmp_path):
    guard, trust = setup(tmp_path)
    key = generate_key()
    message = protect_bytes(b"valid", key)
    old = trust.read()
    # Simulates an external advance that persisted while local DB did not.
    trust.advance(old, b"z" * 32)
    with pytest.raises(StateIntegrityError):
        guard.recover_once(message, key)
    with sqlite3.connect(guard.database) as conn:
        assert conn.execute("SELECT count(*) FROM seen").fetchone()[0] == 0
