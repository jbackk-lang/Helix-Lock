"""Compact representation of Helix phase symbols (NOT encryption).

Four QPSK symbol indices fit into a byte. Winding is shared metadata,
not 12 floating-point samples per symbol. This is lossless *symbol*
packing, not compression of arbitrary payload entropy.
"""
from __future__ import annotations

import hashlib
import struct

MAGIC = b"HNC1"
HEADER = struct.Struct(">4sBQ32s")
MAX_BYTES = 64 * 1024 * 1024


def encode_compact(data: bytes, *, handedness: int = 1) -> bytes:
    if handedness not in (-1, 1):
        raise ValueError("handedness must be +1 or -1")
    if len(data) > MAX_BYTES:
        raise ValueError("research format size limit")
    # Every input byte already contains exactly four two-bit QPSK indices.
    # This format stores the indices rather than redundant phase samples.
    return HEADER.pack(MAGIC, 1 if handedness == 1 else 0, len(data),
                       hashlib.sha256(data).digest()) + data


def decode_compact(encoded: bytes) -> tuple[bytes, int]:
    if len(encoded) < HEADER.size:
        raise ValueError("truncated header")
    magic, sign, length, digest = HEADER.unpack_from(encoded)
    if magic != MAGIC or sign not in (0, 1) or length > MAX_BYTES:
        raise ValueError("invalid compact format")
    if len(encoded) != HEADER.size + length:
        raise ValueError("invalid payload length")
    payload = encoded[HEADER.size:]
    if hashlib.sha256(payload).digest() != digest:
        raise ValueError("corruption detected; digest is NOT authentication")
    return payload, (1 if sign else -1)
