"""Experimental reversible TIMDR-inspired branch transform search.

Research only: no encryption, no HLOM format changes. Score includes a
2-byte selector per candidate. Never use test-set scores as production claims.
Run: python -m experiments.omega_branch_search
"""
from __future__ import annotations

import json
import random
import zlib

LAGS = (1, 2, 3, 4, 16, 256)
LANES = (1, 2, 3, 4, 8)


def split(data: bytes, lanes: int) -> bytes:
    return b"".join(data[i::lanes] for i in range(lanes))


def unsplit(data: bytes, lanes: int) -> bytes:
    counts = [len(range(i, len(data), lanes)) for i in range(lanes)]
    offsets = [sum(counts[:i]) for i in range(lanes)]
    parts = [data[offsets[i]:offsets[i] + counts[i]] for i in range(lanes)]
    return bytes(parts[i % lanes][i // lanes] for i in range(len(data)))


def forward(data: bytes, *, lanes: int = 1, lag: int = 1,
            method: str = "raw") -> bytes:
    if lanes not in LANES or lag not in LAGS or method not in ("raw", "xor", "sub"):
        raise ValueError("invalid transform")
    stream = split(data, lanes)
    if method == "raw":
        return stream
    if method == "xor":
        return bytes(value ^ (stream[i - lag] if i >= lag else 0)
                     for i, value in enumerate(stream))
    return bytes((value - (stream[i - lag] if i >= lag else 0)) % 256
                 for i, value in enumerate(stream))


def inverse(data: bytes, *, lanes: int = 1, lag: int = 1,
            method: str = "raw") -> bytes:
    if lanes not in LANES or lag not in LAGS or method not in ("raw", "xor", "sub"):
        raise ValueError("invalid transform")
    if method == "raw":
        return unsplit(data, lanes)
    restored = bytearray()
    for value in data:
        prior = restored[-lag] if len(restored) >= lag else 0
        restored.append((value ^ prior) if method == "xor" else (value + prior) % 256)
    return unsplit(bytes(restored), lanes)


def search(data: bytes, level: int = 6) -> dict:
    baseline = len(zlib.compress(data, level))
    rows = []
    for lanes in LANES:
        for method in ("raw", "xor", "sub"):
            for lag in ((1,) if method == "raw" else LAGS):
                encoded = forward(data, lanes=lanes, lag=lag, method=method)
                assert inverse(encoded, lanes=lanes, lag=lag, method=method) == data
                compressed = len(zlib.compress(encoded, level))
                rows.append({"lanes": lanes, "method": method, "lag": lag,
                             "zlib_bytes": compressed,
                             "estimated_bytes_with_selector": compressed + 2})
    rows.sort(key=lambda x: (x["estimated_bytes_with_selector"], x["lanes"],
                             x["method"], x["lag"]))
    return {"input_bytes": len(data), "baseline_zlib_bytes": baseline,
            "best": rows[0], "top10": rows[:10],
            "net_gain_bytes": baseline - rows[0]["estimated_bytes_with_selector"]}


def main() -> None:
    rng = random.Random(42)
    size = 32768
    samples = {
        "random": rng.randbytes(size),
        "gradient": bytes(i % 256 for i in range(size)),
        "rows": bytes(((i // 256) * 3 + i % 256) % 256 for i in range(size)),
        "rgb": bytes((i // 3 + (0, 30, 60)[i % 3]) % 256 for i in range(size)),
        "periodic": b"ABCD" * (size // 4),
    }
    for name, data in samples.items():
        print(json.dumps({"sample": name, **search(data)}, sort_keys=True))


if __name__ == "__main__":
    main()
