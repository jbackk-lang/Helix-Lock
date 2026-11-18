"""Ensure the optimized OBX1 delta transform is byte-identical to v1."""
import random

import pytest

from experiments.omega_block_codec import _sub, _encode, _decode, pack, unpack


def reference_sub(data: bytes, lag: int) -> bytes:
    return bytes((value - (data[i - lag] if i >= lag else 0)) & 255
                 for i, value in enumerate(data))


@pytest.mark.parametrize("lag", [1, 3, 8, 256])
@pytest.mark.parametrize("size", [0, 1, 2, 7, 8, 255, 256, 257, 1024, 32768])
def test_delta_matches_original_reference(lag, size):
    data = random.Random(size * 1009 + lag).randbytes(size)
    assert _sub(data, lag) == reference_sub(data, lag)


@pytest.mark.parametrize("mode", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("size", [0, 1, 255, 256, 257, 4096])
def test_modes_remain_reversible(mode, size):
    data = random.Random(size * 17 + mode).randbytes(size)
    assert _decode(_encode(data, mode), mode) == data


@pytest.mark.parametrize("size", [0, 1, 32768, 32769])
def test_archive_roundtrip_after_optimization(size):
    data = random.Random(size).randbytes(size)
    assert unpack(pack(data)) == data
