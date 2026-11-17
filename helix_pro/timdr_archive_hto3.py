"""HTO3 experimental resilient envelope for the existing HTO2 Helix archive.

Three independently authenticated, fixed-size headers permit recovery from
one or two corrupted header copies. The payload remains a complete HTO2
archive (including its two authenticated indexes and GF256 parity).
This is a compatibility wrapper, not a new compression algorithm.
"""
import hashlib
import hmac
import struct

from .timdr_archive_hto2 import pack as pack_hto2, unpack as unpack_hto2

MAGIC = b"HTO3"
HEADER_SIZE = 4 + 8 + 32
HEADER_COPIES = 3
PREFIX_SIZE = HEADER_SIZE * HEADER_COPIES
MAX_ARCHIVE_SIZE = 1 << 34


class EnvelopeError(ValueError):
    pass


def _tag(key, header):
    if len(key) != 32:
        raise EnvelopeError("expected a 32-byte Helix key")
    derived = hmac.digest(key, b"HTO3 envelope header v1", "sha256")
    return hmac.digest(derived, header, "sha256")


def pack(data: bytes, key: bytes, block_size: int = 65536) -> bytes:
    inner = pack_hto2(data, key, block_size=block_size)
    if len(inner) > MAX_ARCHIVE_SIZE:
        raise EnvelopeError("archive too large")
    header = MAGIC + struct.pack(">Q", len(inner))
    framed = header + _tag(key, header)
    return framed * HEADER_COPIES + inner


def unpack(archive: bytes, key: bytes):
    if len(archive) < PREFIX_SIZE:
        raise EnvelopeError("truncated envelope")
    valid = []
    for i in range(HEADER_COPIES):
        block = archive[i * HEADER_SIZE:(i + 1) * HEADER_SIZE]
        header, tag = block[:12], block[12:]
        if header[:4] == MAGIC and hmac.compare_digest(_tag(key, header), tag):
            length = struct.unpack(">Q", header[4:12])[0]
            if length <= MAX_ARCHIVE_SIZE and PREFIX_SIZE + length == len(archive):
                valid.append(length)
    if not valid:
        raise EnvelopeError("no valid authenticated header or incorrect archive size")
    if len(set(valid)) != 1:
        raise EnvelopeError("conflicting authenticated headers")
    return unpack_hto2(archive[PREFIX_SIZE:], key)
