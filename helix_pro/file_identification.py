"""Read-only, unauthenticated file header identification for the desktop UI.

A matching magic/version does NOT prove authenticity or successful decryption.
"""
from __future__ import annotations

import struct


def identify_header(header: bytes) -> tuple[str, int | None]:
    """Return (display label, unverified counter) without reading file contents."""
    if len(header) >= 13 and header[:5] == b"HLXC\x01":
        return "CounterLock / HLXC", struct.unpack(">Q", header[5:13])[0]
    if len(header) >= 6 and header[:5] == b"HLOB\x01" and header[5] in (1, 2):
        return "Experimental OBX1 / HLOB", None
    if len(header) >= 6 and header[:5] == b"HLOM\x01" and header[5] in (1, 2):
        return "Experimental Omega / HLOM", None
    if header[:4] == b"HLXN":
        return "Helix named / HLXN", None
    if header[:4] == b"HLXP":
        return "Helix / HLXP", None
    return "Unknown / plain file", None
