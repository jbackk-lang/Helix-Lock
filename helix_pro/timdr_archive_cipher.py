"""Opt-in Helix-Omega file encryption using the experimental HTO4 archive.

This is a file-level integration, NOT a replacement for AES-256-GCM.
Existing HLXP/HLXN files and cipher.py defaults remain unchanged.
"""
from __future__ import annotations

import os
import struct

from .cipher import derive_key_from_password, HelixProError
from .timdr_archive_fast import pack as pack_fast
from .timdr_archive_hto4 import pack as pack_mode, unpack as unpack_hto4

MAGIC = b"HLOM"
VERSION = 1
KEY_MODE = 1
PASSWORD_MODE = 2
SALT_SIZE = 16


def encrypt_file_omega(in_path: str, out_path: str, *, key: bytes | None = None,
                       password: str | None = None, block_size: int = 65536,
                       predictor: str = "fast") -> None:
    """Encrypt a file through TIMDR predictors + HTO2/3 + AES-GCM.

    predictor='fast' selects on an 8 KiB sample; raw/1d/2d/3d/auto
    select an explicit HTO4 mode. A new format prevents confusion with HLXP.
    """
    if (key is None) == (password is None):
        raise HelixProError("provide exactly one of key or password")
    if key is not None:
        if len(key) != 32:
            raise HelixProError("key must contain 32 bytes")
        mode, salt, secret = KEY_MODE, b"", key
    else:
        salt = os.urandom(SALT_SIZE)
        mode, secret = PASSWORD_MODE, derive_key_from_password(password, salt)
    with open(in_path, "rb") as f:
        plaintext = f.read()
    if predictor == "fast":
        archive = pack_fast(plaintext, secret, block_size=block_size)
    else:
        archive = pack_mode(plaintext, secret, block_size=block_size, mode=predictor)
    with open(out_path, "wb") as f:
        f.write(MAGIC + bytes((VERSION, mode)) + salt + archive)


def decrypt_file_omega(in_path: str, out_path: str, *, key: bytes | None = None,
                       password: str | None = None) -> int:
    """Restore a HLOM file; return number of repaired encrypted data blocks.

    No output is written if authentication, recovery or decoding fails.
    """
    if (key is None) == (password is None):
        raise HelixProError("provide exactly one of key or password")
    with open(in_path, "rb") as f:
        data = f.read()
    if len(data) < 6 or data[:4] != MAGIC or data[4] != VERSION:
        raise HelixProError("not a supported Helix-Omega file")
    mode = data[5]
    if mode == KEY_MODE:
        if key is None or len(key) != 32:
            raise HelixProError("this archive requires a 32-byte key")
        secret, archive = key, data[6:]
    elif mode == PASSWORD_MODE:
        if password is None or len(data) < 6 + SALT_SIZE:
            raise HelixProError("this archive requires a password and salt")
        secret = derive_key_from_password(password, data[6:22])
        archive = data[22:]
    else:
        raise HelixProError("unknown Helix-Omega key mode")
    try:
        plaintext, repaired = unpack_hto4(archive, secret)
    except (ValueError, IndexError, KeyError, TypeError, struct.error) as exc:
        raise HelixProError("authentication, recovery or decoding failed") from exc
    with open(out_path, "wb") as f:
        f.write(plaintext)
    return repaired
