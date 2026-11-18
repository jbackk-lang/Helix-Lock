"""Explore independent predictors per branch, with honest selector overhead.

Research only: not a production HLOM codec. No cryptographic claims.
Run: python -m experiments.omega_branch_independent
"""
from __future__ import annotations

import json
import random
import zlib

from experiments.omega_branch_search import LAGS, LANES, split, unsplit, forward

METHODS = ("raw", "xor", "sub")
CHOICES = [("raw", 1)] + [(method, lag) for method in ("xor", "sub") for lag in LAGS]


def branch_lengths(size: int, lanes: int) -> list[int]:
    return [len(range(i, size, lanes)) for i in range(lanes)]


def encode_lane(data: bytes, method: str, lag: int) -> bytes:
    return forward(data, lanes=1, lag=lag, method=method)


def decode_lane(data: bytes, method: str, lag: int) -> bytes:
    from experiments.omega_branch_search import inverse
    return inverse(data, lanes=1, lag=lag, method=method)


def encode_independent(data: bytes, lanes: int, selectors: list[tuple[str, int]]) -> bytes:
    if lanes not in LANES or len(selectors) != lanes:
        raise ValueError("invalid branch count or selectors")
    separated = split(data, lanes)
    lengths = branch_lengths(len(data), lanes)
    pos, result = 0, bytearray()
    for length, (method, lag) in zip(lengths, selectors):
        result.extend(encode_lane(separated[pos:pos + length], method, lag))
        pos += length
    return bytes(result)


def decode_independent(data: bytes, lanes: int, selectors: list[tuple[str, int]]) -> bytes:
    if lanes not in LANES or len(selectors) != lanes:
        raise ValueError("invalid branch count or selectors")
    lengths = branch_lengths(len(data), lanes)
    pos, result = 0, bytearray()
    for length, (method, lag) in zip(lengths, selectors):
        result.extend(decode_lane(data[pos:pos + length], method, lag))
        pos += length
    return unsplit(bytes(result), lanes)


def search(data: bytes, level: int = 6) -> dict:
    baseline = len(zlib.compress(data, level))
    results = []
    for lanes in LANES:
        separated = split(data, lanes)
        lengths = branch_lengths(len(data), lanes)
        pos, selectors = 0, []
        # Greedy per-lane selection: proxy for final joint zlib compression.
        for length in lengths:
            part = separated[pos:pos + length]
            pos += length
            best = min(CHOICES, key=lambda c: (len(zlib.compress(encode_lane(part, *c), level)), c))
            selectors.append(best)
        encoded = encode_independent(data, lanes, selectors)
        assert decode_independent(encoded, lanes, selectors) == data
        compressed = len(zlib.compress(encoded, level))
        # 1 byte lane count + 1 byte per selector (13 possibilities).
        results.append({"lanes": lanes, "selectors": selectors,
                        "zlib_bytes": compressed,
                        "estimated_bytes_with_selectors": compressed + 1 + lanes})
    results.sort(key=lambda x: (x["estimated_bytes_with_selectors"], x["lanes"]))
    return {"input_bytes": len(data), "baseline_zlib_bytes": baseline,
            "best": results[0], "all_branch_counts": results,
            "net_gain_bytes": baseline - results[0]["estimated_bytes_with_selectors"]}


def main() -> None:
    rng = random.Random(42)
    n = 32768
    samples = {
        "random": rng.randbytes(n),
        "gradient": bytes(i % 256 for i in range(n)),
        "rows": bytes(((i // 256) * 3 + i % 256) % 256 for i in range(n)),
        "rgb": bytes((i // 3 + (0, 30, 60)[i % 3]) % 256 for i in range(n)),
        "periodic": b"ABCD" * (n // 4),
        "mixed_channels": bytes((i // 3 + (0, 100, (i // 3) % 7)[i % 3]) % 256
                                for i in range(n)),
    }
    for name, data in samples.items():
        print(json.dumps({"sample": name, **search(data)}, sort_keys=True))


if __name__ == "__main__":
    main()
