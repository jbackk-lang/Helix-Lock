"""Matched QPSK symbol/byte recovery benchmark; not a security test.

Compare independent symbol decoding to temporal smoothing. Random QPSK payload
symbols are independent, so smoothing may hurt: a deliberate negative control.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
import random
import statistics
import time
from pathlib import Path

from experiments.helix_chiral_intelligence import HelixChiralIntelligence, Observation
from experiments.helix_chiral_signal import transmit


def benchmark(*, sizes=(16, 64, 256), trials=12, noise_levels=(0.12, 0.5, 0.9),
              windows=(1, 3, 7), seed=20261108):
    results = []
    for sigma in noise_levels:
        for size in sizes:
            for window in windows:
                rows = []
                for trial in range(trials):
                    rng = random.Random(seed + size * 1009 + trial)
                    payload = rng.randbytes(size)
                    symbols = [(byte >> shift) & 3 for byte in payload for shift in (6, 4, 2, 0)]
                    observer = HelixChiralIntelligence()
                    history = deque(maxlen=window)
                    decoded = []
                    correct = decided = 0
                    t0 = time.perf_counter()
                    for i, symbol in enumerate(symbols):
                        angles, phases = transmit(symbol, 1, sensors=12, noise=sigma,
                                                  seed=seed + trial * 1000003 + i)
                        assessment = observer.observe(
                            Observation(float(i), tuple(angles), tuple(phases), 0.0))
                        if assessment.symbol is not None:
                            history.append(assessment.symbol)
                        if window == 1:
                            guess = assessment.symbol
                        else:
                            # Temporal mode baseline: most common recent QPSK symbol.
                            # Independent payloads provide no reason to expect improvement.
                            counts = [history.count(j) for j in range(4)]
                            best = max(counts, default=0)
                            winners = [j for j, count in enumerate(counts) if count == best and best > 0]
                            guess = assessment.symbol if assessment.symbol in winners else (
                                winners[0] if len(winners) == 1 else None)
                        decoded.append(guess)
                        correct += guess == symbol
                        decided += guess is not None
                    recovered = None
                    if all(x is not None for x in decoded):
                        recovered = bytes(
                            (decoded[i] << 6) | (decoded[i+1] << 4) |
                            (decoded[i+2] << 2) | decoded[i+3]
                            for i in range(0, len(decoded), 4))
                    rows.append({"symbol_accuracy": correct / len(symbols),
                                 "coverage": decided / len(symbols),
                                 "whole_file": recovered == payload,
                                 "seconds": time.perf_counter() - t0})
                results.append({
                    "noise": sigma, "input_bytes": size, "window": window,
                    "trials": trials,
                    "symbol_accuracy": statistics.mean(r["symbol_accuracy"] for r in rows),
                    "coverage": statistics.mean(r["coverage"] for r in rows),
                    "whole_file_success": sum(r["whole_file"] for r in rows) / trials,
                    "decode_seconds_median": statistics.median(r["seconds"] for r in rows),
                })
    return {"format": "helix-qpsk-memory-benchmark-v1", "seed": seed,
            "note": "Random independent QPSK symbols; temporal voting is a negative control. "
                    "Whole-file success requires all symbols correct. Synthetic phase noise; "
                    "not encryption or a trained model.", "results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-qpsk-memory-benchmark.json"))
    args = parser.parse_args()
    result = benchmark()
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
