"""Opt-in OBX1 + AES-256-GCM file envelope (HLOB v1).

Experimental; distinct from HLOM, HLXP and HLXN. No GF(256) repair.
Entire file is held in memory. No streaming, production security audit or GUI.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .cipher import HelixProError, derive_key_from_password
from experiments.omega_block_codec import pack, unpack

MAGIC = b"HLOB"
VERSION = 1
KEY_MODE = 1
PASSWORD_MODE = 2
SALT_SIZE = 16
NONCE_SIZE = 12
MAX_OUTPUT = 256 * 1024 * 1024


def _secret(key: bytes | None, password: str | None, salt: bytes) -> bytes:
    if (key is None) == (password is None):
        raise HelixProError("provide exactly one of key or password")
    if key is not None:
        if not isinstance(key, bytes) or len(key) != 32:
            raise HelixProError("key must be 32 bytes")
        return key
    if not isinstance(password, str):
        raise HelixProError("password must be a string")
    return derive_key_from_password(password, salt)


def _atomic_write(destination: str | os.PathLike[str], data: bytes) -> None:
    target = Path(destination)
    fd, temporary = tempfile.mkstemp(prefix=".helix-obx-", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def encrypt_file_obx(in_path: str, out_path: str, *,
                     key: bytes | None = None, password: str | None = None,
                     block_size: int = 32768) -> None:
    """Encrypt OBX1 blocks with authenticated header as AES-GCM AAD."""
    if os.path.abspath(in_path) == os.path.abspath(out_path):
        raise HelixProError("input and output paths must differ")
    mode = KEY_MODE if key is not None else PASSWORD_MODE
    salt = os.urandom(SALT_SIZE) if mode == PASSWORD_MODE else b""
    secret = _secret(key, password, salt)
    data = Path(in_path).read_bytes()
    if len(data) > MAX_OUTPUT:
        raise HelixProError("input exceeds experimental size limit")
    packed = pack(data, block_size=block_size)
    nonce = os.urandom(NONCE_SIZE)
    header = MAGIC + bytes((VERSION, mode)) + salt + nonce
    encrypted = AESGCM(secret).encrypt(nonce, packed, header)
    _atomic_write(out_path, header + encrypted)


def decrypt_file_obx(in_path: str, out_path: str, *,
                     key: bytes | None = None, password: str | None = None,
                     max_output_bytes: int = MAX_OUTPUT) -> None:
    """Authenticate before decompressing; never write plaintext on failure."""
    if os.path.abspath(in_path) == os.path.abspath(out_path):
        raise HelixProError("input and output paths must differ")
    data = Path(in_path).read_bytes()
    if len(data) < 6 + NONCE_SIZE + 16 or data[:4] != MAGIC or data[4] != VERSION:
        raise HelixProError("invalid HLOB header")
    mode = data[5]
    if mode not in (KEY_MODE, PASSWORD_MODE):
        raise HelixProError("invalid HLOB key mode")
    if (mode == KEY_MODE and key is None) or (mode == PASSWORD_MODE and password is None):
        raise HelixProError("wrong credential type")
    salt_end = 6 + (SALT_SIZE if mode == PASSWORD_MODE else 0)
    nonce_end = salt_end + NONCE_SIZE
    if len(data) < nonce_end + 16:
        raise HelixProError("truncated HLOB archive")
    secret = _secret(key, password, data[6:salt_end])
    header = data[:nonce_end]
    try:
        packed = AESGCM(secret).decrypt(data[salt_end:nonce_end],
                                       data[nonce_end:], header)
        plaintext = unpack(packed, max_output_bytes=max_output_bytes)
    except (ValueError, OverflowError) as exc:
        raise HelixProError("HLOB authentication or decoding failed") from exc
    except Exception as exc:
        from cryptography.exceptions import InvalidTag
        if isinstance(exc, InvalidTag):
            raise HelixProError("HLOB authentication failed") from exc
        raise
    _atomic_write(out_path, plaintext)
