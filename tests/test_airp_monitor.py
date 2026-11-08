import pytest

from helix_pro.airp_monitor import AIRPMonitor, RepresentationState
from helix_pro.cipher import HelixProError


def test_monitor_verifies_current_representation():
    blob = b"ciphertext-v1"
    state = RepresentationState(1, "key-v1", AIRPMonitor.fingerprint(blob))
    monitor = AIRPMonitor(state)
    assert monitor.verify_current(blob, version=1, key_id="key-v1")
    assert not monitor.verify_current(blob, version=0, key_id="key-v1")
    assert not monitor.verify_current(b"modified", version=1, key_id="key-v1")
    assert not monitor.verify_current(blob, version=1, key_id="key-v2")


def test_monitor_accepts_only_next_version_and_new_key_id():
    blob = b"ciphertext-v1"
    monitor = AIRPMonitor(RepresentationState(1, "key-v1", AIRPMonitor.fingerprint(blob)))
    new_state = monitor.accept_rotation(b"ciphertext-v2", new_version=2, new_key_id="key-v2")
    assert new_state.version == 2
    assert monitor.verify_current(b"ciphertext-v2", version=2, key_id="key-v2")
    with pytest.raises(HelixProError):
        monitor.accept_rotation(b"v3", new_version=4, new_key_id="key-v3")
    with pytest.raises(HelixProError):
        monitor.accept_rotation(b"v3", new_version=3, new_key_id="key-v2")


def test_monitor_records_only_allowlisted_outcomes():
    monitor = AIRPMonitor(RepresentationState(1, "key-v1", "abc"))
    event = monitor.record_access(outcome="denied")
    assert event.outcome == "denied"
    assert len(monitor.events) == 1
    with pytest.raises(HelixProError):
        monitor.record_access(outcome="password=secret")
