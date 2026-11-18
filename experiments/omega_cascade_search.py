"""Explore cascaded reversible predictors and independently compressed branches.

Experimental only; does not change HLOM. Scores include a compact estimated
selector/header budget, but exclude encryption, parity, and archive metadata.
Run: python -m experiments.omega_cascade_search
"""
from __future__ import annotations

import json
import random
import zlib

from experiments.omega_branch_search import LANES, LAGS, split, unsplit, forward, inverse

STAGES = [("raw", 1)] + [(m, lag) for m in ("sub", "xor") for lag in (1, 3, 256)]


def transform(data: bytes, lanes: int, stages: tuple[tuple[str, int], ...]) -> bytes:
    if lanes not in LANES or not 1 <= len(stages) <= 2:
        raise ValueError("invalid branch count or stage count")
    stream = split(data, lanes)
    for method, lag in stages:
        stream = forward(stream, method=method, lag=lag)
    return stream


def restore(data: bytes, lanes: int, stages: tuple[tuple[str, int], ...]) -> bytes:
    if lanes not in LANES or not 1 <= len(stages) <= 2:
        raise ValueError("invalid branch count or stage count")
    for method, lag in reversed(stages):
        data = inverse(data, method=method, lag=lag)
    return unsplit(data, lanes)


def compress_branches(data: bytes, lanes: int, level: int = 6) -> int:
    """Sum separate zlib streams; 1-byte framing estimate per branch."""
    if lanes not in LANES:
        raise ValueError("invalid lanes")
    return sum(len(zlib.compress(data[i::lanes], level)) + 1
               for i in range(lanes))


def search(data: bytes, level: int = 6) -> dict:
    baseline = len(zlib.compress(data, level))
    best = {"bytes": baseline, "lanes": 1, "stages": [["raw", 1]],
            "compression": "raw_zlib"}
    candidates = 0
    for lanes in LANES:
        for first in STAGES:
            for stages in ((first,), *((first, second) for second in STAGES)):
                encoded = transform(data, lanes, stages)
                assert restore(encoded, lanes, stages) == data
                # 1-byte lane count + 1-byte stage count + 1 byte per stage.
                overhead = 2 + len(stages)
                for kind, compressed in (
                    ("joint_zlib", len(zlib.compress(encoded, level))),
                    ("separate_zlib", compress_branches(encoded, lanes, level)),
                ):
                    candidates += 1
                    score = compressed + overhead
                    if score < best["bytes"]:
                        best = {"bytes": score, "lanes": lanes,
                                "stages": [list(stage) for stage in stages],
                                "compression": kind}
    return {"input_bytes": len(data), "baseline_bytes": baseline,
            "best": best, "gain_bytes": baseline - best["bytes"],
            "candidates": candidates}


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
