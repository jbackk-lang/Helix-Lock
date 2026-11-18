import os

import pytest

from helix_pro import generate_key
from helix_pro.cipher import HelixProError
from helix_pro.timdr_archive_cipher import (
    MAGIC, encrypt_file_omega, decrypt_file_omega,
)


@pytest.mark.parametrize("data", [b"", b"ABCD" * 5000, os.urandom(18000)])
@pytest.mark.parametrize("predictor", ["fast", "raw", "1d", "2d", "3d"])
def test_key_file_roundtrip(tmp_path, data, predictor):
    source = tmp_path / "original.bin"
    encrypted = tmp_path / "encrypted.hlom"
    restored = tmp_path / "restored.bin"
    source.write_bytes(data)
    key = generate_key()
    encrypt_file_omega(source, encrypted, key=key, predictor=predictor, block_size=4096)
    assert encrypted.read_bytes().startswith(MAGIC)
    assert decrypt_file_omega(encrypted, restored, key=key) == 0
    assert restored.read_bytes() == data


def test_password_file_roundtrip(tmp_path):
    source = tmp_path / "input"
    encrypted = tmp_path / "encrypted"
    restored = tmp_path / "restored"
    source.write_bytes(b"password archive" * 1000)
    encrypt_file_omega(source, encrypted, password="correct horse battery staple")
    assert decrypt_file_omega(encrypted, restored, password="correct horse battery staple") == 0
    assert restored.read_bytes() == source.read_bytes()


def test_wrong_key_does_not_write_output(tmp_path):
    source = tmp_path / "input"
    encrypted = tmp_path / "encrypted"
    restored = tmp_path / "restored"
    source.write_bytes(b"secret" * 1000)
    encrypt_file_omega(source, encrypted, key=generate_key())
    with pytest.raises(HelixProError):
        decrypt_file_omega(encrypted, restored, key=generate_key())
    assert not restored.exists()


def test_tamper_does_not_write_output(tmp_path):
    source = tmp_path / "input"
    encrypted = tmp_path / "encrypted"
    restored = tmp_path / "restored"
    source.write_bytes(b"secret" * 1000)
    key = generate_key()
    encrypt_file_omega(source, encrypted, key=key)
    damaged = bytearray(encrypted.read_bytes())
    damaged[6 + 4] ^= 1  # authenticated HTO4 predictor selector
    encrypted.write_bytes(damaged)
    with pytest.raises(HelixProError):
        decrypt_file_omega(encrypted, restored, key=key)
    assert not restored.exists()


def test_invalid_credentials(tmp_path):
    source = tmp_path / "input"
    source.write_bytes(b"abc")
    with pytest.raises(HelixProError):
        encrypt_file_omega(source, tmp_path / "encrypted")
    with pytest.raises(HelixProError):
        encrypt_file_omega(source, tmp_path / "encrypted", key=b"short")
