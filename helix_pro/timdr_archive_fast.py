"""Sampled, conservative predictor selector for HTO4.

Selects on an 8 KiB prefix instead of transforming the entire input four
times. The threshold intentionally prefers raw on marginal gains.
"""
import zlib
from .timdr_archive_hto4 import MODES, transform, pack as _pack, unpack

SAMPLE_SIZE = 8192
MIN_GAIN_BYTES = 64


def choose_mode(data: bytes) -> str:
    sample = data[:SAMPLE_SIZE]
    if len(sample) < 4096:
        return "raw"
    raw_size = len(zlib.compress(sample))
    if raw_size < len(sample) // 2:
        return "raw"
    sizes = {"raw": raw_size}
    for mode in MODES[1:]:
        sizes[mode] = len(zlib.compress(transform(sample, mode)))
    best = min(sizes, key=sizes.get)
    return best if sizes[best] + MIN_GAIN_BYTES < raw_size else "raw"


def pack(data: bytes, key: bytes, block_size: int = 65536):
    return _pack(data, key, block_size=block_size, mode=choose_mode(data))
