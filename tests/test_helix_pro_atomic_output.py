"""Atomic publication and malformed-header regressions for the supported core format."""
import os

import pytest

from helix_pro.cipher import (
    atomic_write_bytes,
    HelixProError,
    decrypt_file,
    decrypt_file_with_name,
    encrypt_file,
    encrypt_file_with_name,
    generate_key,
)


def test_encrypt_failure_before_replace_preserves_existing_target(tmp_path, monkeypatch):
    source = tmp_path / "plain.txt"
    target = tmp_path / "existing.helixpro"
    source.write_bytes(b"new plaintext")
    target.write_bytes(b"previous target")
    def fail_replace(*args):
        raise OSError("simulated replace failure")
    monkeypatch.setattr("helix_pro.cipher.os.replace", fail_replace)
    with pytest.raises(OSError):
        encrypt_file(str(source), str(target), key=generate_key())
    assert target.read_bytes() == b"previous target"
    assert not list(tmp_path.glob(".helix-*.tmp"))


def test_decrypt_authentication_failure_preserves_existing_target(tmp_path):
    source = tmp_path / "plain.txt"
    encrypted = tmp_path / "encrypted.helixpro"
    target = tmp_path / "existing.txt"
    source.write_bytes(b"authenticated payload")
    key = generate_key()
    encrypt_file(str(source), str(encrypted), key=key)
    target.write_bytes(b"previous target")
    damaged = bytearray(encrypted.read_bytes())
    damaged[-1] ^= 1
    encrypted.write_bytes(damaged)
    with pytest.raises(HelixProError):
        decrypt_file(str(encrypted), str(target), key=key)
    assert target.read_bytes() == b"previous target"
    assert not list(tmp_path.glob(".helix-*.tmp"))


@pytest.mark.parametrize("payload", [b"", b"HLXP", b"HLXP\x01", b"HLXN", b"HLXN\x01"])
def test_truncated_headers_raise_domain_error_not_index_error(tmp_path, payload):
    source = tmp_path / "truncated.helixpro"
    target = tmp_path / "output.bin"
    source.write_bytes(payload)
    with pytest.raises(HelixProError):
        decrypt_file(str(source), str(target), key=generate_key())
    with pytest.raises(HelixProError):
        decrypt_file_with_name(str(source), str(tmp_path), key=generate_key())
    assert not target.exists()


def test_named_decrypt_publishes_only_verified_content(tmp_path):
    source = tmp_path / "document.txt"
    encrypted = tmp_path / "document.helixpro"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    source.write_bytes(b"complete verified file")
    key = generate_key()
    encrypt_file_with_name(str(source), str(encrypted), key=key)
    output = decrypt_file_with_name(str(encrypted), str(out_dir), key=key)
    assert open(output, "rb").read() == source.read_bytes()



def test_public_atomic_writer_preserves_target_on_replace_error(tmp_path, monkeypatch):
    target = tmp_path / "existing.bin"
    target.write_bytes(b"keep me")
    def fail_replace(*args):
        raise OSError("simulated publication failure")
    monkeypatch.setattr("helix_pro.cipher.os.replace", fail_replace)
    with pytest.raises(OSError):
        atomic_write_bytes(str(target), b"new bytes")
    assert target.read_bytes() == b"keep me"
    assert not list(tmp_path.glob(".helix-*.tmp"))



def test_named_encrypt_replace_failure_preserves_existing_target(tmp_path, monkeypatch):
    source = tmp_path / "plain.txt"
    target = tmp_path / "existing.helixpro"
    source.write_bytes(b"new plaintext")
    target.write_bytes(b"previous encrypted target")

    def fail_replace(*args):
        raise OSError("simulated replace failure")

    monkeypatch.setattr("helix_pro.cipher.os.replace", fail_replace)
    with pytest.raises(OSError):
        encrypt_file_with_name(str(source), str(target), key=generate_key())

    assert target.read_bytes() == b"previous encrypted target"
    assert not list(tmp_path.glob(".helix-*.tmp"))
