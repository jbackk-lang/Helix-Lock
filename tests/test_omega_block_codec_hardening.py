"""Adversarial malformed-input and resource-limit checks for OBX1."""
import struct

import pytest

from experiments.omega_block_codec import pack, unpack, HEADER, ENTRY


def test_output_limit_accepts_exact_and_rejects_smaller():
    data = b"abcdef" * 200
    archive = pack(data)
    assert unpack(archive, max_output_bytes=len(data)) == data
    with pytest.raises(ValueError, match="limit"):
        unpack(archive, max_output_bytes=len(data) - 1)


@pytest.mark.parametrize("limit", [-1, True, 1.5, None])
def test_invalid_limit(limit):
    with pytest.raises(ValueError, match="limit"):
        unpack(pack(b"x"), max_output_bytes=limit)


def test_impossible_count_rejected_before_iteration():
    archive = bytearray(pack(b"x"))
    struct.pack_into(">I", archive, 8, 1000000)
    with pytest.raises(ValueError):
        unpack(bytes(archive))


def test_corrupted_zlib_is_normalized_to_value_error():
    archive = bytearray(pack(b"abc" * 300))
    archive[HEADER.size + ENTRY.size] = 0
    with pytest.raises(ValueError, match="compressed block"):
        unpack(bytes(archive))


def test_invalid_raw_length_rejected():
    archive = bytearray(pack(b"abc"))
    struct.pack_into(">I", archive, HEADER.size + 1, 100000)
    with pytest.raises(ValueError, match="invalid entry"):
        unpack(bytes(archive))


def test_no_extra_bytes_after_stream():
    with pytest.raises(ValueError):
        unpack(pack(b"hello") + b"garbage")


def test_empty_roundtrip_with_zero_limit():
    assert unpack(pack(b""), max_output_bytes=0) == b""
