"""Regression tests for the experimental TIMDR / Helix archive bridge."""
import os
import pytest

from helix_pro import generate_key
from helix_pro.timdr_archive_bridge import ArchiveError, pack, unpack, _parse


@pytest.mark.parametrize("data", [b"", b"abc" * 40000, bytes(range(256)) * 600, os.urandom(140000)])
def test_roundtrip(data):
    key = generate_key()
    restored, repaired = unpack(pack(data, key), key)
    assert restored == data
    assert repaired == 0


def test_one_ciphertext_erasure_is_recovered():
    key = generate_key()
    original = os.urandom(5 * 4096)
    archive = bytearray(pack(original, key, block_size=4096))
    info, payload = _parse(bytes(archive), key)
    offset_base = len(archive) - len(payload)
    target = info["groups"][0]["blocks"][1]
    archive[offset_base + target["offset"] + 3] ^= 0x80
    restored, repaired = unpack(bytes(archive), key)
    assert restored == original
    assert repaired == 1


def test_two_erasures_rejected():
    key = generate_key()
    archive = bytearray(pack(os.urandom(16000), key, block_size=4096))
    info, payload = _parse(bytes(archive), key)
    base = len(archive) - len(payload)
    for item in info["groups"][0]["blocks"][:2]:
        archive[base + item["offset"] + 3] ^= 0x80
    with pytest.raises(ArchiveError):
        unpack(bytes(archive), key)


def test_wrong_key_and_metadata_tampering_rejected():
    key = generate_key()
    archive = bytearray(pack(b"data" * 1000, key))
    with pytest.raises(ArchiveError):
        unpack(bytes(archive), generate_key())
    archive[10] ^= 1
    with pytest.raises(ArchiveError):
        unpack(bytes(archive), key)
