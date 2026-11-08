import json
import sqlite3

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from helix_pro.airp_ledger import AIRPIntegrityLedger, GENESIS_HASH
from helix_pro.cipher import HelixProError


class MemoryAnchor:
    """Test double; production anchor must be independently administered."""

    def __init__(self):
        self.value = None

    def publish_checkpoint(self, checkpoint):
        parsed = json.loads(checkpoint)
        if self.value is not None:
            old = json.loads(self.value)
            if parsed["sequence"] < old["sequence"]:
                raise HelixProError("anchor rejects checkpoint rollback")
            if parsed["sequence"] == old["sequence"] and parsed["head_hash"] != old["head_hash"]:
                raise HelixProError("anchor rejects checkpoint fork")
        self.value = checkpoint

    def latest_checkpoint(self):
        return self.value


def _ledger(tmp_path, anchor=None):
    key = Ed25519PrivateKey.generate()
    ledger = AIRPIntegrityLedger(tmp_path / "ledger.sqlite3", key, trust_anchor=anchor)
    return ledger, key


def test_hash_chain_and_signed_checkpoint(tmp_path):
    anchor = MemoryAnchor()
    ledger, key = _ledger(tmp_path, anchor)
    first = ledger.append("registered", "object-1", {"version": 1, "blob_sha256": "a" * 64})
    second = ledger.append("rotated", "object-1", {"version": 2, "blob_sha256": "b" * 64})
    assert first["previous_hash"] == GENESIS_HASH
    assert second["previous_hash"] == first["event_hash"]
    assert ledger.verify_chain()
    checkpoint = ledger.publish_checkpoint()
    parsed = AIRPIntegrityLedger.verify_checkpoint(checkpoint, ledger.public_key_bytes)
    assert parsed["sequence"] == 2
    assert ledger.verify().status == "fully_anchored"


def test_tampered_event_breaks_chain(tmp_path):
    ledger, _ = _ledger(tmp_path)
    ledger.append("registered", "object-1", {"version": 1})
    with sqlite3.connect(ledger.database_path) as db:
        db.execute("UPDATE airp_ledger_events SET payload_json='{\"version\":99}' WHERE sequence=1")
    assert not ledger.verify_chain()
    assert ledger.verify().status == "local_chain_invalid"


def test_external_checkpoint_detects_local_database_rollback(tmp_path):
    anchor = MemoryAnchor()
    ledger, _ = _ledger(tmp_path, anchor)
    ledger.append("registered", "object-1", {"version": 1})
    ledger.publish_checkpoint()
    ledger.append("rotated", "object-1", {"version": 2})
    ledger.publish_checkpoint()
    with sqlite3.connect(ledger.database_path) as db:
        db.execute("DELETE FROM airp_ledger_events WHERE sequence > 1")
    result = ledger.verify()
    assert not result.valid
    assert result.status == "local_rollback_detected"
    assert result.anchored_sequence == 2


def test_local_suffix_is_reported_until_anchored(tmp_path):
    anchor = MemoryAnchor()
    ledger, _ = _ledger(tmp_path, anchor)
    ledger.append("registered", "object-1", {"version": 1})
    ledger.publish_checkpoint()
    ledger.append("access", "object-1", {"outcome": "granted"})
    assert ledger.verify().status == "valid_with_unanchored_suffix"


def test_checkpoint_rejects_wrong_pinned_public_key(tmp_path):
    ledger, _ = _ledger(tmp_path)
    checkpoint = ledger.create_checkpoint()
    other_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    with pytest.raises(HelixProError, match="signer"):
        AIRPIntegrityLedger.verify_checkpoint(checkpoint, other_key)


def test_counterlock_replay_is_rejected_by_ledger(tmp_path):
    from helix_pro.airp_counter import AIRPCounterLock
    from helix_pro.counter_lock import CounterLock

    ledger, _ = _ledger(tmp_path)
    key = b"k" * 32
    guard = AIRPCounterLock(key, ledger, "counter-object")
    lock = CounterLock(key)
    original = lock.lock(b"payload", counter=0)
    plaintext, counter, next_blob = guard.unlock_and_advance(original)
    assert (plaintext, counter) == (b"payload", 0)
    with pytest.raises(HelixProError, match="replay"):
        guard.unlock_and_advance(original)
    plaintext2, counter2, _ = guard.unlock_and_advance(next_blob)
    assert (plaintext2, counter2) == (b"payload", 1)
