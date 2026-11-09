"""Experimental bounded-memory authenticated streaming file envelope HNS1.

Independent AES-256-GCM records with unique nonces and sequence-bound AAD.
An authenticated final record binds total plaintext bytes and record count.
Decrypt to a temporary file; publish only after final authentication.
Not wire-compatible with HNA1. No replay protection or key management.
"""
from __future__ import annotations

import os
from pathlib import Path
import struct
import tempfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"HNS1"
CHUNK = 64 * 1024
HEADER = struct.Struct(">4s8sI")
RECORD = struct.Struct(">BI")
FINAL = struct.Struct(">QQ")
MAX_RECORDS = 2**32 - 2


def _ensure_distinct_files(source: Path, target: Path) -> None:
    """Reject path, symlink, and hard-link aliases before publishing output."""
    if source.resolve() == target.resolve():
        raise ValueError("input and output must differ")
    try:
        if target.exists() and os.path.samefile(source, target):
            raise ValueError("input and output must not refer to the same file")
    except OSError:
        # A missing target is normal; permission and filesystem errors are
        # handled by the subsequent open/replace operation.
        pass


def _nonce(prefix: bytes, sequence: int) -> bytes:
    return prefix + struct.pack(">I", sequence)


def _aad(header: bytes, sequence: int, kind: int) -> bytes:
    return b"helix-stream-v1" + header + struct.pack(">IB", sequence, kind)


def encrypt_file(source: str | Path, target: str | Path, key: bytes) -> None:
    source, target = Path(source), Path(target)
    _ensure_distinct_files(source, target)
    if len(key) != 32:
        raise ValueError("AES-256-GCM requires 32-byte key")
    prefix = os.urandom(8)
    header = HEADER.pack(MAGIC, prefix, CHUNK)
    aes = AESGCM(key)
    temporary = None
    try:
        with source.open("rb") as src, tempfile.NamedTemporaryFile(
            mode="wb", dir=target.parent, prefix=".helix-stream-",
            suffix=".tmp", delete=False
        ) as dst:
            temporary = Path(dst.name)
            dst.write(header)
            count = 0
            total = 0
            while True:
                data = src.read(CHUNK)
                if not data:
                    break
                if count >= MAX_RECORDS:
                    raise ValueError("stream record limit exceeded")
                encrypted = aes.encrypt(_nonce(prefix, count),
                                        data, _aad(header, count, 0))
                dst.write(RECORD.pack(0, len(encrypted)))
                dst.write(encrypted)
                count += 1
                total += len(data)
            trailer = aes.encrypt(_nonce(prefix, count), FINAL.pack(count, total),
                                  _aad(header, count, 1))
            dst.write(RECORD.pack(1, len(trailer)))
            dst.write(trailer)
            dst.flush()
            os.fsync(dst.fileno())
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def decrypt_file(source: str | Path, target: str | Path, key: bytes) -> None:
    source, target = Path(source), Path(target)
    _ensure_distinct_files(source, target)
    if len(key) != 32:
        raise ValueError("AES-256-GCM requires 32-byte key")
    temporary = None
    try:
        with source.open("rb") as src:
            header = src.read(HEADER.size)
            if len(header) != HEADER.size:
                raise ValueError("truncated stream header")
            magic, prefix, chunk_size = HEADER.unpack(header)
            if magic != MAGIC or chunk_size != CHUNK:
                raise ValueError("unsupported stream format")
            aes = AESGCM(key)
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=target.parent, prefix=".helix-stream-",
                suffix=".tmp", delete=False
            ) as dst:
                temporary = Path(dst.name)
                count = 0
                total = 0
                while True:
                    record_header = src.read(RECORD.size)
                    if len(record_header) != RECORD.size:
                        raise ValueError("missing authenticated final record")
                    kind, length = RECORD.unpack(record_header)
                    if kind == 0:
                        if length < 17 or length > CHUNK + 16 or count >= MAX_RECORDS:
                            raise ValueError("invalid encrypted chunk length")
                    elif kind == 1:
                        if length != FINAL.size + 16:
                            raise ValueError("invalid final record length")
                    else:
                        raise ValueError("unknown record type")
                    ciphertext = src.read(length)
                    if len(ciphertext) != length:
                        raise ValueError("truncated encrypted record")
                    plaintext = aes.decrypt(_nonce(prefix, count), ciphertext,
                                            _aad(header, count, kind))
                    if kind == 1:
                        expected_count, expected_total = FINAL.unpack(plaintext)
                        if expected_count != count or expected_total != total:
                            raise ValueError("invalid final stream totals")
                        if src.read(1):
                            raise ValueError("trailing bytes after final record")
                        break
                    dst.write(plaintext)
                    total += len(plaintext)
                    count += 1
                dst.flush()
                os.fsync(dst.fileno())
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
