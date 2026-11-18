"""OBX1 block framing, exact recovery and malformed input tests."""
import random
import zlib

import pytest

from experiments.omega_block_codec import pack, unpack


@pytest.mark.parametrize("size", [0, 1, 2, 3, 255, 256, 257, 4096, 32768, 32769, 65536])
@pytest.mark.parametrize("kind", ["random", "gradient", "rows"])
@pytest.mark.parametrize("block_size", [1024, 32768])
def test_roundtrip(size, kind, block_size):
    rng = random.Random(42 + size)
    data = {
        "random": lambda: rng.randbytes(size),
        "gradient": lambda: bytes(i % 256 for i in range(size)),
        "rows": lambda: bytes(((i // 256) * 3 + i % 256) % 256 for i in range(size)),
    }[kind]()
    assert unpack(pack(data, block_size=block_size)) == data


@pytest.mark.parametrize("bad", [
    b"",
    b"NOPE" + pack(b"hello")[4:],
    pack(b"hello")[:-1],
    pack(b"hello") + b"extra",
])
def test_reject_bad_archive(bad):
    with pytest.raises(ValueError):
        unpack(bad)


def test_full_header_overhead_counted():
    data = bytes(range(256)) * 128
    packed = pack(data)
    assert packed.startswith(b"OBX1")
    assert unpack(packed) == data
    assert len(packed) < len(zlib.compress(data))


def test_invalid_block_size():
    with pytest.raises(ValueError):
        pack(b"abc", block_size=0)
