"""Experimental TIMDR-Omega / Helix-Lock archive bridge.

Format HTO1: magic(4) | metadata_length(4, big endian) | canonical JSON
metadata | HMAC-SHA256(metadata) | concatenated encrypted blocks.
Each group contains four encrypted zlib-compressed data blocks and one
XOR parity block. The parity is computed over ciphertext, BEFORE decrypt.
This is an experimental single-erasure code, not a production archive.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import struct
import zlib

from .cipher import encrypt_bytes, decrypt_bytes

MAGIC = b"HTO1"
BLOCK_SIZE = 65536
GROUP_SIZE = 4


class ArchiveError(ValueError):
    pass


def _auth_key(key: bytes) -> bytes:
    if len(key) != 32:
        raise ArchiveError("expected a 32-byte Helix key")
    return hmac.digest(key, b"HTO1 metadata authentication v1", "sha256")


def _xor(parts: list[bytes]) -> bytes:
    width = max(map(len, parts), default=0)
    out = bytearray(width)
    for part in parts:
        for i, value in enumerate(part):
            out[i] ^= value
    return bytes(out)


def _json(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pack(data: bytes, key: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    """Compress, encrypt each segment with Helix AES-GCM, then add XOR parity."""
    _auth_key(key)
    if not 1 <= block_size <= 1024 * 1024:
        raise ValueError("invalid block_size")
    chunks = [data[i:i + block_size] for i in range(0, len(data), block_size)]
    groups, payload = [], bytearray()
    for start in range(0, len(chunks), GROUP_SIZE):
        encrypted = [encrypt_bytes(zlib.compress(c), key, aad=b"HTO1:data:v1")
                     for c in chunks[start:start + GROUP_SIZE]]
        blocks = encrypted + [_xor(encrypted)]
        descriptors = []
        for blob in blocks:
            descriptors.append({
                "offset": len(payload), "length": len(blob),
                "sha256": hashlib.sha256(blob).hexdigest()
            })
            payload.extend(blob)
        groups.append({"raw_lengths": [len(c) for c in chunks[start:start + GROUP_SIZE]],
                       "blocks": descriptors})
    metadata = _json({"version": 1, "total": len(data), "block_size": block_size,
                      "groups": groups})
    if len(metadata) > 64 * 1024 * 1024:
        raise ArchiveError("metadata too large")
    tag = hmac.digest(_auth_key(key), metadata, "sha256")
    return MAGIC + struct.pack(">I", len(metadata)) + metadata + tag + payload


def _parse(archive: bytes, key: bytes):
    _auth_key(key)
    if len(archive) < 40 or archive[:4] != MAGIC:
        raise ArchiveError("invalid archive magic")
    size = struct.unpack(">I", archive[4:8])[0]
    if size > 64 * 1024 * 1024 or len(archive) < 40 + size:
        raise ArchiveError("invalid metadata length")
    metadata = archive[8:8 + size]
    tag = archive[8 + size:40 + size]
    if not hmac.compare_digest(tag, hmac.digest(_auth_key(key), metadata, "sha256")):
        raise ArchiveError("metadata authentication failed")
    info = json.loads(metadata)
    if info.get("version") != 1 or not isinstance(info.get("groups"), list):
        raise ArchiveError("unsupported archive metadata")
    return info, memoryview(archive)[40 + size:]


def unpack(archive: bytes, key: bytes) -> tuple[bytes, int]:
    """Return (original bytes, repaired ciphertext segments). Fail closed."""
    info, payload = _parse(archive, key)
    output = bytearray()
    repaired = 0
    for group in info["groups"]:
        lengths = group["raw_lengths"]
        desc = group["blocks"]
        if not (1 <= len(lengths) <= GROUP_SIZE and len(desc) == len(lengths) + 1):
            raise ArchiveError("invalid group layout")
        blocks = []
        for item in desc:
            offset, length = item["offset"], item["length"]
            if not (isinstance(offset, int) and isinstance(length, int)
                    and offset >= 0 and length >= 0 and offset + length <= len(payload)):
                raise ArchiveError("invalid block bounds")
            blob = bytes(payload[offset:offset + length])
            blocks.append(blob if hashlib.sha256(blob).hexdigest() == item["sha256"] else None)
        missing = [i for i, blob in enumerate(blocks[:-1]) if blob is None]
        if missing:
            if len(missing) != 1 or blocks[-1] is None:
                raise ArchiveError("too many damaged blocks in group")
            index = missing[0]
            recovered = _xor([blocks[-1]] + [b for i, b in enumerate(blocks[:-1])
                                             if i != index and b is not None])
            recovered = recovered[:desc[index]["length"]]
            if hashlib.sha256(recovered).hexdigest() != desc[index]["sha256"]:
                raise ArchiveError("recovered ciphertext checksum mismatch")
            blocks[index] = recovered
            repaired += 1
        for blob, expected in zip(blocks[:-1], lengths):
            try:
                raw = zlib.decompress(decrypt_bytes(blob, key, aad=b"HTO1:data:v1"))
            except Exception as exc:
                raise ArchiveError("ciphertext authentication or decompression failed") from exc
            if len(raw) != expected:
                raise ArchiveError("raw block length mismatch")
            output.extend(raw)
    if len(output) != info["total"]:
        raise ArchiveError("total output length mismatch")
    return bytes(output), repaired
