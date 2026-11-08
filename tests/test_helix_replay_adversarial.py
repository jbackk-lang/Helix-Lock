"""Adversarial regression tests for the opt-in replay guard.

The guard protects one durable SQLite state domain. Deleting or restoring an
old database is explicitly outside its security guarantees.
"""
from concurrent.futures import ThreadPoolExecutor
import shutil

import pytest
from cryptography.exceptions import InvalidTag

from experiments.helix_native_replay_guard import ReplayDetected, ReplayGuard
from experiments.helix_native_secure_envelope import generate_key, protect_bytes


def test_concurrent_identical_message_only_one_acceptance(tmp_path):
    db = tmp_path / "concurrent.sqlite"
    key = generate_key()
    envelope = protect_bytes(b"one-time authorization", key)
    guard = ReplayGuard(db)

    def attempt(_):
        try:
            guard.recover_once(envelope, key)
            return "accepted"
        except ReplayDetected:
            return "replayed"

    with ThreadPoolExecutor(max_workers=12) as executor:
        outcomes = list(executor.map(attempt, range(48)))
    assert outcomes.count("accepted") == 1
    assert outcomes.count("replayed") == 47


def test_distinct_messages_accepted_under_contention(tmp_path):
    db = tmp_path / "distinct.sqlite"
    key = generate_key()
    guard = ReplayGuard(db)
    messages = [protect_bytes(i.to_bytes(4, "big"), key) for i in range(32)]

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda msg: guard.recover_once(msg, key)[0], messages))
    assert results == [i.to_bytes(4, "big") for i in range(32)]


def test_wrong_key_cannot_poison_replay_state(tmp_path):
    guard = ReplayGuard(tmp_path / "state.sqlite")
    key = generate_key()
    envelope = protect_bytes(b"valid", key)
    with pytest.raises(InvalidTag):
        guard.recover_once(envelope, generate_key())
    assert guard.recover_once(envelope, key)[0] == b"valid"


@pytest.mark.xfail(strict=True, reason="SQLite state rollback is not protected by this design")
def test_restored_old_database_allows_replay_known_limitation(tmp_path):
    db = tmp_path / "state.sqlite"
    guard = ReplayGuard(db)
    key = generate_key()
    envelope = protect_bytes(b"first", key)
    # Snapshot the empty DB before accepting the envelope.
    backup = tmp_path / "old.sqlite"
    shutil.copyfile(db, backup)
    guard.recover_once(envelope, key)
    # Adversary can restore the older database state.
    shutil.copyfile(backup, db)
    with pytest.raises(ReplayDetected):
        ReplayGuard(db).recover_once(envelope, key)
