"""Reproducible Helix Native codec benchmark and negative controls.

The reported rates describe this Python prototype, not a secure cipher.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import time
from pathlib import Path

from experiments.helix_native_codec import decode_bytes, encode_bytes


def perturb(encoded: bytes, *, sigma: float, seed: int) -> bytes:
    if sigma < 0 or not math.isfinite(sigma):
        raise ValueError("sigma must be finite and nonnegative")
    rng = random.Random(seed)
    doc = json.loads(encoded)
    for _, phases in doc["records"]:
        for j in range(len(phases)):
            phases[j] += rng.gauss(0, sigma)
    return json.dumps(doc, separators=(",", ":"), allow_nan=False).encode()


def benchmark(*, sizes=(16, 64, 256), trials=3, noise_levels=(0.0, 0.12, 0.5),
              seed=20261108):
    if trials < 1 or any(n < 0 for n in sizes):
        raise ValueError("invalid benchmark dimensions")
    results = []
    for size in sizes:
        samples = []
        for trial in range(trials):
            rng = random.Random(seed + size * 1009 + trial)
            payload = rng.randbytes(size)
            t0 = time.perf_counter()
            encoded = encode_bytes(payload)
            t1 = time.perf_counter()
            recovered = decode_bytes(encoded)
            t2 = time.perf_counter()
            if recovered != payload:
                raise AssertionError("clean roundtrip failed")
            noise_results = {}
            for sigma in noise_levels:
                altered = perturb(encoded, sigma=sigma, seed=seed + trial)
                try:
                    success = decode_bytes(altered) == payload
                except (ValueError, TypeError, KeyError, IndexError):
                    success = False
                noise_results[str(sigma)] = success
            samples.append({"encoded_bytes": len(encoded),
                            "encode_seconds": t1 - t0,
                            "decode_seconds": t2 - t1,
                            "noise_success": noise_results})
        results.append({
            "input_bytes": size,
            "trials": trials,
            "encoded_bytes_median": statistics.median(x["encoded_bytes"] for x in samples),
            "expansion_ratio_median": (statistics.median(x["encoded_bytes"] for x in samples) / size
                                       if size else None),
            "encode_seconds_median": statistics.median(x["encode_seconds"] for x in samples),
            "decode_seconds_median": statistics.median(x["decode_seconds"] for x in samples),
            "noise_roundtrip_rate": {
                str(sigma): sum(x["noise_success"][str(sigma)] for x in samples) / trials
                for sigma in noise_levels},
        })
    return {"format": "helix-native-benchmark-v0", "seed": seed,
            "warning": "Research codec is reversible without a key; no security claims.",
            "results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-native-benchmark.json"))
    args = parser.parse_args()
    report = benchmark()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
