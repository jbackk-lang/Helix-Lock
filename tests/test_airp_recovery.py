import pytest

from helix_pro.airp_recovery import generate_recovery_key, unwrap_data_key, wrap_data_key
from helix_pro.cipher import HelixProError


def test_recovery_key_envelope_round_trip():
    recovery_key = generate_recovery_key()
    data_key = b"d" * 32
    envelope = wrap_data_key(data_key, recovery_key, object_id="object-1", key_id="key-v1")
    assert unwrap_data_key(envelope, recovery_key, object_id="object-1", key_id="key-v1") == data_key


def test_recovery_key_envelope_rejects_wrong_key_and_context():
    recovery_key = generate_recovery_key()
    envelope = wrap_data_key(b"d" * 32, recovery_key, object_id="object-1", key_id="key-v1")
    with pytest.raises(HelixProError, match="authentication"):
        unwrap_data_key(envelope, generate_recovery_key(), object_id="object-1", key_id="key-v1")
    with pytest.raises(HelixProError, match="authentication"):
        unwrap_data_key(envelope, recovery_key, object_id="object-2", key_id="key-v1")
