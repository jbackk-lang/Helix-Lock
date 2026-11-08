"""Recovery-key envelopes for Helix Pro data keys.

The caller supplies and independently stores a random 256-bit recovery key.
This module never writes recovery material to disk and never derives it from a
human password. Protect the recovery key separately (offline/KMS/HSM).
"""
from __future__ import annotations

import os
import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .cipher import KEY_SIZE, HelixProError

MAGIC = b"HLRK"
VERSION = 1
NONCE_SIZE = 12
HEADER = MAGIC + bytes([VERSION])


def generate_recovery_key() -> bytes:
    """Generate a 256-bit recovery key; caller must store it outside this device."""
    return os.urandom(KEY_SIZE)


def _aad(object_id: str, key_id: str) -> bytes:
    if not object_id or len(object_id) > 512 or not key_id or len(key_id) > 256:
        raise HelixProError("object_id and key_id must be non-empty and within limits")
    return b"Helix-Lock/AIRP/recovery/v1\0" + object_id.encode("utf-8") + b"\0" + key_id.encode("utf-8")


def wrap_data_key(data_key: bytes, recovery_key: bytes, *, object_id: str, key_id: str) -> bytes:
    """Encrypt a 256-bit data key under an externally held recovery key."""
    if len(data_key) != KEY_SIZE or len(recovery_key) != KEY_SIZE:
        raise HelixProError("data_key and recovery_key must each be 32 bytes")
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(recovery_key).encrypt(nonce, data_key, _aad(object_id, key_id))
    return HEADER + nonce + ciphertext


def unwrap_data_key(envelope: bytes, recovery_key: bytes, *, object_id: str, key_id: str) -> bytes:
    """Recover a data key only with the matching recovery key and object metadata."""
    if len(recovery_key) != KEY_SIZE:
        raise HelixProError("recovery_key must be 32 bytes")
    if not isinstance(envelope, bytes) or len(envelope) < len(HEADER) + NONCE_SIZE + 16:
        raise HelixProError("invalid AIRP recovery envelope")
    if envelope[:len(HEADER)] != HEADER:
        raise HelixProError("unknown AIRP recovery envelope format")
    nonce_start = len(HEADER)
    nonce = envelope[nonce_start:nonce_start + NONCE_SIZE]
    ciphertext = envelope[nonce_start + NONCE_SIZE:]
    try:
        data_key = AESGCM(recovery_key).decrypt(nonce, ciphertext, _aad(object_id, key_id))
    except Exception as exc:
        raise HelixProError("AIRP data-key recovery authentication failed") from exc
    if len(data_key) != KEY_SIZE:
        raise HelixProError("recovered data key has an invalid length")
    return data_key
