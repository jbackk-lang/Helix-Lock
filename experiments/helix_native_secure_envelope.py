"""Authenticated file envelope around the experimental Helix symbol format.

Security is provided by standard AES-256-GCM, NOT by Helix phase encoding.
Requires the 'cryptography' package. A fresh 32-byte key must be generated
and stored separately; this module deliberately does not accept passwords.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from experiments.helix_native_compact import decode_compact, encode_compact

MAGIC = b"HNA1"
AAD = b"helix-native-authenticated-envelope-v1"
NONCE_BYTES = 12
KEY_BYTES = 32


def generate_key() -> bytes:
    return AESGCM.generate_key(bit_length=256)


def protect_bytes(data: bytes, key: bytes, *, handedness: int = 1) -> bytes:
    if len(key) != KEY_BYTES:
        raise ValueError("AES-256-GCM requires a 32-byte key")
    nonce = os.urandom(NONCE_BYTES)
    compact = encode_compact(data, handedness=handedness)
    ciphertext = AESGCM(key).encrypt(nonce, compact, AAD + MAGIC)
    return MAGIC + nonce + ciphertext


def recover_bytes(envelope: bytes, key: bytes) -> tuple[bytes, int]:
    if len(key) != KEY_BYTES:
        raise ValueError("AES-256-GCM requires a 32-byte key")
    if len(envelope) < len(MAGIC) + NONCE_BYTES + 16:
        raise ValueError("truncated authenticated envelope")
    if envelope[:len(MAGIC)] != MAGIC:
        raise ValueError("unsupported authenticated envelope")
    nonce = envelope[len(MAGIC):len(MAGIC) + NONCE_BYTES]
    ciphertext = envelope[len(MAGIC) + NONCE_BYTES:]
    compact = AESGCM(key).decrypt(nonce, ciphertext, AAD + MAGIC)
    return decode_compact(compact)


def _atomic_write(target: Path, data: bytes) -> None:
    """Write in destination directory, fsync, then replace atomically.

    Prevents partial destination contents on ordinary write errors. Atomic
    replacement does not by itself guarantee directory metadata durability
    after power loss, nor protect against hostile concurrent path replacement.
    """
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=target.parent,
                                         prefix=".helix-", suffix=".tmp",
                                         delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def protect_file(source: str | Path, target: str | Path, key: bytes) -> None:
    source, target = Path(source), Path(target)
    if source.resolve() == target.resolve():
        raise ValueError("input and output must differ")
    _atomic_write(target, protect_bytes(source.read_bytes(), key))


def recover_file(source: str | Path, target: str | Path, key: bytes) -> None:
    source, target = Path(source), Path(target)
    if source.resolve() == target.resolve():
        raise ValueError("input and output must differ")
    # Authenticate fully before creating the destination.
    decoded, _ = recover_bytes(source.read_bytes(), key)
    _atomic_write(target, decoded)
