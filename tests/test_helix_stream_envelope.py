import os

import pytest
from cryptography.exceptions import InvalidTag

from experiments.helix_stream_envelope import encrypt_file, decrypt_file, HEADER, RECORD


@pytest.mark.parametrize("size", [0, 1, 65535, 65536, 65537, 200000])
def test_stream_roundtrip(tmp_path, size):
    src, enc, out = (tmp_path / name for name in ("in", "enc", "out"))
    src.write_bytes(os.urandom(size))
    key = os.urandom(32)
    encrypt_file(src, enc, key)
    decrypt_file(enc, out, key)
    assert out.read_bytes() == src.read_bytes()


def test_wrong_key_does_not_replace_existing_output(tmp_path):
    src, enc, out = (tmp_path / name for name in ("in", "enc", "out"))
    src.write_bytes(os.urandom(70000))
    out.write_bytes(b"old")
    encrypt_file(src, enc, os.urandom(32))
    with pytest.raises(InvalidTag):
        decrypt_file(enc, out, os.urandom(32))
    assert out.read_bytes() == b"old"


@pytest.mark.parametrize("mutation", ["truncate", "tamper", "append"])
def test_stream_mutation_rejected_without_publication(tmp_path, mutation):
    src, enc, out = (tmp_path / name for name in ("in", "enc", "out"))
    src.write_bytes(os.urandom(130000))
    out.write_bytes(b"old")
    key = os.urandom(32)
    encrypt_file(src, enc, key)
    data = bytearray(enc.read_bytes())
    if mutation == "truncate":
        data = data[:-10]
    elif mutation == "tamper":
        data[HEADER.size + RECORD.size + 2] ^= 1
    else:
        data += b"extra"
    enc.write_bytes(data)
    with pytest.raises((ValueError, InvalidTag)):
        decrypt_file(enc, out, key)
    assert out.read_bytes() == b"old"
    assert not list(tmp_path.glob(".helix-stream-*.tmp"))


def test_header_tamper_rejected(tmp_path):
    src, enc, out = (tmp_path / name for name in ("in", "enc", "out"))
    src.write_bytes(b"secret")
    key = os.urandom(32)
    encrypt_file(src, enc, key)
    data = bytearray(enc.read_bytes())
    data[4] ^= 1
    enc.write_bytes(data)
    with pytest.raises(InvalidTag):
        decrypt_file(enc, out, key)
    assert not out.exists()
