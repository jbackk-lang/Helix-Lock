import os

import pytest
from cryptography.exceptions import InvalidTag

from experiments.helix_native_secure_envelope import (
    generate_key, protect_bytes, recover_bytes, protect_file, recover_file,
)


@pytest.mark.parametrize("data", [b"", b"Helix", bytes(range(256)), b"\\x00" * 256])
@pytest.mark.parametrize("handedness", [-1, 1])
def test_authenticated_roundtrip(data, handedness):
    key = generate_key()
    envelope = protect_bytes(data, key, handedness=handedness)
    assert recover_bytes(envelope, key) == (data, handedness)
    assert data != envelope


def test_wrong_key_fails():
    envelope = protect_bytes(b"private", generate_key())
    with pytest.raises(InvalidTag):
        recover_bytes(envelope, generate_key())


def test_ciphertext_tampering_fails():
    key = generate_key()
    envelope = bytearray(protect_bytes(b"private", key))
    envelope[-1] ^= 1
    with pytest.raises(InvalidTag):
        recover_bytes(bytes(envelope), key)


def test_nonce_tampering_fails():
    key = generate_key()
    envelope = bytearray(protect_bytes(b"private", key))
    envelope[5] ^= 1
    with pytest.raises(InvalidTag):
        recover_bytes(bytes(envelope), key)


def test_fresh_nonce():
    key = generate_key()
    assert protect_bytes(b"same", key) != protect_bytes(b"same", key)


def test_wrong_key_does_not_create_file(tmp_path):
    source = tmp_path / "source.bin"
    envelope = tmp_path / "encrypted.hna"
    recovered = tmp_path / "recovered.bin"
    source.write_bytes(os.urandom(1024))
    protect_file(source, envelope, generate_key())
    with pytest.raises(InvalidTag):
        recover_file(envelope, recovered, generate_key())
    assert not recovered.exists()


def test_real_file_roundtrip(tmp_path):
    source = tmp_path / "source.bin"
    envelope = tmp_path / "encrypted.hna"
    recovered = tmp_path / "recovered.bin"
    source.write_bytes(os.urandom(4096))
    key = generate_key()
    protect_file(source, envelope, key)
    recover_file(envelope, recovered, key)
    assert recovered.read_bytes() == source.read_bytes()


def test_refuses_same_source_and_target(tmp_path):
    source = tmp_path / "same.bin"
    source.write_bytes(b"data")
    with pytest.raises(ValueError):
        protect_file(source, source, generate_key())
