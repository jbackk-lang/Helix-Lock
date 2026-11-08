import os
from unittest.mock import patch

import pytest
from cryptography.exceptions import InvalidTag

from experiments.helix_native_secure_envelope import (
    generate_key, protect_file, recover_file,
)


def test_atomic_roundtrip_and_replacement(tmp_path):
    source = tmp_path / "source.bin"
    encrypted = tmp_path / "encrypted.hna"
    recovered = tmp_path / "recovered.bin"
    source.write_bytes(os.urandom(2048))
    recovered.write_bytes(b"previous")
    key = generate_key()
    protect_file(source, encrypted, key)
    recover_file(encrypted, recovered, key)
    assert recovered.read_bytes() == source.read_bytes()
    assert not list(tmp_path.glob(".helix-*.tmp"))


def test_failed_replace_preserves_existing_target(tmp_path):
    source = tmp_path / "source.bin"
    target = tmp_path / "target.hna"
    source.write_bytes(b"new secret")
    target.write_bytes(b"previous safe contents")
    with patch("experiments.helix_native_secure_envelope.os.replace",
               side_effect=OSError("simulated replacement failure")):
        with pytest.raises(OSError):
            protect_file(source, target, generate_key())
    assert target.read_bytes() == b"previous safe contents"
    assert not list(tmp_path.glob(".helix-*.tmp"))


def test_failed_recovery_preserves_existing_target(tmp_path):
    source = tmp_path / "source.bin"
    encrypted = tmp_path / "encrypted.hna"
    target = tmp_path / "existing.bin"
    source.write_bytes(b"secret")
    target.write_bytes(b"existing")
    protect_file(source, encrypted, generate_key())
    with pytest.raises(InvalidTag):
        recover_file(encrypted, target, generate_key())
    assert target.read_bytes() == b"existing"
    assert not list(tmp_path.glob(".helix-*.tmp"))


def test_failed_fsync_preserves_existing_target(tmp_path):
    source = tmp_path / "source.bin"
    target = tmp_path / "target.hna"
    source.write_bytes(b"secret")
    target.write_bytes(b"existing")
    with patch("experiments.helix_native_secure_envelope.os.fsync",
               side_effect=OSError("simulated fsync failure")):
        with pytest.raises(OSError):
            protect_file(source, target, generate_key())
    assert target.read_bytes() == b"existing"
    assert not list(tmp_path.glob(".helix-*.tmp"))
