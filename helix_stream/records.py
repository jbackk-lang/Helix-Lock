"""Experimental authenticated record framing for Helix Stream.

This is a low-level prototype, NOT a complete network protocol. The caller must
supply a fresh, independent 32-byte key for each session and direction. Never
reuse a key with a reset sequence counter. Key establishment, peer identity,
replay across reconnects, transport and flow control are out of scope.
"""
from __future__ import annotations

import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"HSR1"
MAX_PLAINTEXT = 64 * 1024
_HEADER = struct.Struct(">BQI")  # kind, sequence, ciphertext length
_KIND_DATA = 0
_KIND_FINAL = 1
_TAG_SIZE = 16
_MAX_SEQUENCE = (1 << 64) - 1


class RecordError(ValueError):
    """Malformed record or invalid stream state."""


class _RecordBase:
    def __init__(self, key: bytes, nonce_salt: bytes, session_id: bytes,
                 direction: bytes):
        if len(key) != 32:
            raise ValueError("a fresh 32-byte session-direction key is required")
        if len(nonce_salt) != 4:
            raise ValueError("nonce_salt must be exactly 4 bytes")
        if not session_id or len(session_id) > 64:
            raise ValueError("session_id must contain 1..64 bytes")
        if not direction or len(direction) > 16:
            raise ValueError("direction label must contain 1..16 bytes")
        self._aes = AESGCM(key)
        self._salt = bytes(nonce_salt)
        self._session_id = bytes(session_id)
        self._direction = bytes(direction)
        self._sequence = 0
        self._closed = False

    def _nonce(self) -> bytes:
        if self._sequence > _MAX_SEQUENCE:
            raise RecordError("record sequence exhausted")
        return self._salt + struct.pack(">Q", self._sequence)

    def _aad(self, header: bytes) -> bytes:
        return MAGIC + bytes([len(self._session_id)]) + self._session_id + bytes(
            [len(self._direction)]
        ) + self._direction + header


class RecordSealer(_RecordBase):
    """Seal ordered records. Use a new key when creating a new session."""

    def seal(self, plaintext: bytes = b"", *, final: bool = False) -> bytes:
        if self._closed:
            raise RecordError("stream is already closed")
        if not isinstance(plaintext, bytes):
            raise TypeError("plaintext must be bytes")
        if len(plaintext) > MAX_PLAINTEXT:
            raise RecordError("record exceeds maximum plaintext size")
        if final and plaintext:
            raise RecordError("final record must not contain application data")
        kind = _KIND_FINAL if final else _KIND_DATA
        cipher_length = len(plaintext) + _TAG_SIZE
        header = _HEADER.pack(kind, self._sequence, cipher_length)
        ciphertext = self._aes.encrypt(
            self._nonce(), plaintext, self._aad(header)
        )
        self._sequence += 1
        if final:
            self._closed = True
        return header + ciphertext


class RecordOpener(_RecordBase):
    """Open strictly ordered records; each returned data record is authenticated."""

    def open(self, frame: bytes) -> tuple[bytes, bool]:
        if self._closed:
            raise RecordError("stream is already closed")
        if not isinstance(frame, bytes) or len(frame) < _HEADER.size + _TAG_SIZE:
            raise RecordError("truncated record")
        header = frame[:_HEADER.size]
        kind, sequence, cipher_length = _HEADER.unpack(header)
        if kind not in (_KIND_DATA, _KIND_FINAL):
            raise RecordError("unknown record type")
        if sequence != self._sequence:
            raise RecordError("unexpected record sequence")
        if cipher_length != len(frame) - _HEADER.size:
            raise RecordError("record length mismatch")
        if cipher_length > MAX_PLAINTEXT + _TAG_SIZE:
            raise RecordError("record exceeds maximum ciphertext size")
        if kind == _KIND_FINAL and cipher_length != _TAG_SIZE:
            raise RecordError("final record must be empty")
        plaintext = self._aes.decrypt(
            self._nonce(), frame[_HEADER.size:], self._aad(header)
        )
        self._sequence += 1
        final = kind == _KIND_FINAL
        if final:
            self._closed = True
        return plaintext, final
