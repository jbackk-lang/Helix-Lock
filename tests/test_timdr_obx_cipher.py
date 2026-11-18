"""HLOB opt-in authenticated OBX1 integration tests."""
import os
import pytest

from helix_pro.cipher import HelixProError
from helix_pro.timdr_obx_cipher import encrypt_file_obx, decrypt_file_obx


@pytest.mark.parametrize("data", [b"", b"hello", bytes(range(256)) * 128, os.urandom(4096)])
def test_key_roundtrip(tmp_path, data):
    source, encrypted, restored = (tmp_path / x for x in ("src", "encrypted", "restored"))
    source.write_bytes(data)
    key = bytes(range(32))
    encrypt_file_obx(str(source), str(encrypted), key=key)
    assert encrypted.read_bytes().startswith(b"HLOB")
    decrypt_file_obx(str(encrypted), str(restored), key=key)
    assert restored.read_bytes() == data


def test_password_roundtrip(tmp_path):
    src, enc, dec = (tmp_path / x for x in ("src", "enc", "dec"))
    src.write_bytes(b"rows" * 400)
    encrypt_file_obx(str(src), str(enc), password="correct horse battery staple")
    decrypt_file_obx(str(enc), str(dec), password="correct horse battery staple")
    assert dec.read_bytes() == src.read_bytes()


def test_wrong_key_preserves_output(tmp_path):
    src, enc, dec = (tmp_path / x for x in ("src", "enc", "dec"))
    src.write_bytes(b"private")
    dec.write_bytes(b"existing")
    encrypt_file_obx(str(src), str(enc), key=b"a" * 32)
    with pytest.raises(HelixProError):
        decrypt_file_obx(str(enc), str(dec), key=b"b" * 32)
    assert dec.read_bytes() == b"existing"


def test_header_tamper_rejected(tmp_path):
    src, enc, dec = (tmp_path / x for x in ("src", "enc", "dec"))
    src.write_bytes(b"private")
    encrypt_file_obx(str(src), str(enc), key=b"a" * 32)
    damaged = bytearray(enc.read_bytes())
    damaged[6] ^= 1
    enc.write_bytes(damaged)
    with pytest.raises(HelixProError):
        decrypt_file_obx(str(enc), str(dec), key=b"a" * 32)
    assert not dec.exists()


def test_output_cap(tmp_path):
    src, enc, dec = (tmp_path / x for x in ("src", "enc", "dec"))
    src.write_bytes(b"Z" * 200)
    encrypt_file_obx(str(src), str(enc), key=b"a" * 32)
    with pytest.raises(HelixProError):
        decrypt_file_obx(str(enc), str(dec), key=b"a" * 32, max_output_bytes=199)
    assert not dec.exists()


def test_same_path_rejected(tmp_path):
    src = tmp_path / "src"
    src.write_bytes(b"keep")
    with pytest.raises(HelixProError):
        encrypt_file_obx(str(src), str(src), key=b"a" * 32)
    assert src.read_bytes() == b"keep"
