"""Experimental reversible block codec; NOT encrypted or HLOM-compatible."""
from __future__ import annotations
import struct
import zlib

MAGIC = b"OBX1"
MAX_BLOCK = 1 << 20
MODES = (0, 1, 2, 3, 4)
HEADER = struct.Struct(">4sII")
ENTRY = struct.Struct(">BII")


def _split(data: bytes, n: int) -> bytes:
    return b"".join(data[i::n] for i in range(n))


def _unsplit(data: bytes, n: int) -> bytes:
    sizes = [len(range(i, len(data), n)) for i in range(n)]
    parts = []
    offset = 0
    for size in sizes:
        parts.append(data[offset:offset + size])
        offset += size
    return bytes(parts[i % n][i // n] for i in range(len(data)))


def _sub(data: bytes, lag: int) -> bytes:
    return bytes((value - (data[i - lag] if i >= lag else 0)) & 255
                 for i, value in enumerate(data))


def _unsub(data: bytes, lag: int) -> bytes:
    result = bytearray()
    for value in data:
        result.append((value + (result[-lag] if len(result) >= lag else 0)) & 255)
    return bytes(result)


def _encode(data: bytes, mode: int) -> bytes:
    if mode == 0:
        return data
    if mode == 1:
        return _sub(data, 1)
    if mode == 2:
        return _sub(_sub(data, 1), 256)
    if mode in (3, 4):
        return _sub(_split(data, 3 if mode == 3 else 8), 1)
    raise ValueError("unknown mode")


def _decode(data: bytes, mode: int) -> bytes:
    if mode == 0:
        return data
    if mode == 1:
        return _unsub(data, 1)
    if mode == 2:
        return _unsub(_unsub(data, 256), 1)
    if mode in (3, 4):
        return _unsplit(_unsub(data, 1), 3 if mode == 3 else 8)
    raise ValueError("unknown mode")


def pack(data: bytes, block_size: int = 32768) -> bytes:
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if not 1 <= block_size <= MAX_BLOCK:
        raise ValueError("invalid block size")
    if len(data) > 0xFFFFFFFF:
        raise ValueError("input too large for format")
    count = (len(data) + block_size - 1) // block_size
    out = bytearray(HEADER.pack(MAGIC, len(data), count))
    for offset in range(0, len(data), block_size):
        block = data[offset:offset + block_size]
        choices = [(len(blob), mode, blob) for mode in MODES
                   for blob in (zlib.compress(_encode(block, mode), 6),)]
        _, mode, compressed = min(choices, key=lambda row: (row[0], row[1]))
        out.extend(ENTRY.pack(mode, len(block), len(compressed)))
        out.extend(compressed)
    return bytes(out)


def unpack(archive: bytes) -> bytes:
    if len(archive) < HEADER.size:
        raise ValueError("truncated header")
    magic, total, count = HEADER.unpack_from(archive)
    if magic != MAGIC or count > total or (total == 0) != (count == 0):
        raise ValueError("invalid header")
    output = bytearray()
    offset = HEADER.size
    for _ in range(count):
        if len(archive) - offset < ENTRY.size:
            raise ValueError("truncated entry")
        mode, raw_len, comp_len = ENTRY.unpack_from(archive, offset)
        offset += ENTRY.size
        if mode not in MODES or not 1 <= raw_len <= MAX_BLOCK or comp_len > len(archive) - offset:
            raise ValueError("invalid entry")
        compressed = archive[offset:offset + comp_len]
        offset += comp_len
        obj = zlib.decompressobj()
        transformed = obj.decompress(compressed, raw_len + 1)
        if len(transformed) != raw_len or not obj.eof or obj.unused_data or obj.unconsumed_tail:
            raise ValueError("invalid compressed block")
        block = _decode(transformed, mode)
        if len(output) + len(block) > total:
            raise ValueError("output exceeds declared length")
        output.extend(block)
    if offset != len(archive) or len(output) != total:
        raise ValueError("archive length mismatch")
    return bytes(output)
