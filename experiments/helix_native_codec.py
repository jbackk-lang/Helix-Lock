"""Helix Native research codec: real file bytes -> synthetic phase symbols.

NOT encryption, authentication, or a secure file format. SHA-256 is an
unkeyed accidental-corruption check, not an authenticity guarantee.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from experiments.helix_chiral_intelligence import HelixChiralIntelligence, Observation
from experiments.helix_chiral_signal import transmit

FORMAT = "helix-native-research-v0"


def encode_bytes(data: bytes, *, handedness: int = 1, sensors: int = 12) -> bytes:
    if handedness not in (-1, 1) or sensors < 2:
        raise ValueError("invalid geometry")
    records = []
    for index, byte in enumerate(data):
        for shift in (6, 4, 2, 0):
            symbol = (byte >> shift) & 3
            angles, phases = transmit(symbol, handedness, sensors=sensors, noise=0,
                                      seed=index * 4 + (6 - shift)//2)
            records.append([angles, phases])
    document = {"format": FORMAT, "length": len(data),
                "sha256": hashlib.sha256(data).hexdigest(), "records": records}
    return json.dumps(document, separators=(",", ":"), allow_nan=False).encode("utf-8")


def decode_bytes(encoded: bytes) -> bytes:
    doc = json.loads(encoded)
    if not isinstance(doc, dict) or doc.get("format") != FORMAT:
        raise ValueError("unsupported research format")
    length = doc.get("length")
    if type(length) is not int or length < 0 or len(doc.get("records", [])) != length * 4:
        raise ValueError("invalid length or record count")
    observer = HelixChiralIntelligence()
    values = []
    for index, record in enumerate(doc["records"]):
        if not isinstance(record, list) or len(record) != 2:
            raise ValueError("invalid record")
        angles, phases = record
        assessment = observer.observe(Observation(float(index), tuple(angles),
                                                   tuple(phases), 0.0))
        if assessment.symbol is None:
            raise ValueError("ambiguous phase symbol")
        values.append(assessment.symbol)
    data = bytes((values[i] << 6) | (values[i+1] << 4) |
                 (values[i+2] << 2) | values[i+3]
                 for i in range(0, len(values), 4))
    if hashlib.sha256(data).hexdigest() != doc.get("sha256"):
        raise ValueError("corruption detected (not authentication)")
    return data


def encode_file(source: str | Path, target: str | Path) -> None:
    Path(target).write_bytes(encode_bytes(Path(source).read_bytes()))


def decode_file(source: str | Path, target: str | Path) -> None:
    # Do not overwrite output unless the entire decode/check succeeds.
    decoded = decode_bytes(Path(source).read_bytes())
    Path(target).write_bytes(decoded)
