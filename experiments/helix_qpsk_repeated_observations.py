"""Repeated independent observations of the SAME QPSK symbol.

Baseline: one observation. Alternatives: circular phase averaging of 3/7
observations, using the known chirality and phase reference. This is redundancy
and signal processing, NOT learned AI, encryption or error correction coding.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import statistics
import time

from experiments.helix_chiral_signal import PHASES, transmit, wrap


def _decode(observations):
    re = im = 0.0
    for angles, phases in observations:
        for a, p in zip(angles, phases):
            residual = p - a  # Known +1 chirality and calibrated phase=0
            re += math.cos(residual)
            im += math.sin(residual)
    phase = math.atan2(im, re)
    distances = [(abs(wrap(phase - target)), index) for index, target in enumerate(PHASES)]
    error, guess = min(distances)
    return guess if error <= math.pi / 8 else None


def benchmark(*, sizes=(16, 64, 256), trials=12,
              noise_levels=(0.12, 0.5, 0.9), repeats=(1, 3, 7),
              seed=20261108, sensors=12):
    if any(x < 1 for x in sizes + repeats) or trials < 1 or sensors < 2:
        raise ValueError("invalid benchmark dimensions")
    results = []
    for sigma in noise_levels:
        for size in sizes:
            for copies in repeats:
                rows = []
                for trial in range(trials):
                    rng = random.Random(seed + size * 1009 + trial)
                    payload = rng.randbytes(size)
                    symbols = [(byte >> shift) & 3 for byte in payload for shift in (6, 4, 2, 0)]
                    correct = decided = 0
                    guesses = []
                    t0 = time.perf_counter()
                    for i, symbol in enumerate(symbols):
                        observations = [
                            transmit(symbol, 1, sensors=sensors, noise=sigma,
                                     seed=seed + trial * 1000003 + i * 101 + copy)
                            for copy in range(copies)
                        ]
                        guess = _decode(observations)
                        guesses.append(guess)
                        correct += guess == symbol
                        decided += guess is not None
                    elapsed = time.perf_counter() - t0
                    recovered = None
                    if all(g is not None for g in guesses):
                        recovered = bytes(
                            (guesses[i] << 6) | (guesses[i+1] << 4) |
                            (guesses[i+2] << 2) | guesses[i+3]
                            for i in range(0, len(guesses), 4))
                    rows.append({"accuracy": correct / len(symbols),
                                 "coverage": decided / len(symbols),
                                 "whole": recovered == payload, "seconds": elapsed})
                results.append({
                    "noise": sigma, "input_bytes": size, "repeats": copies,
                    "trials": trials,
                    "symbol_accuracy": statistics.mean(r["accuracy"] for r in rows),
                    "coverage": statistics.mean(r["coverage"] for r in rows),
                    "whole_file_success": sum(r["whole"] for r in rows) / trials,
                    "elapsed_seconds_median": statistics.median(r["seconds"] for r in rows),
                    "raw_phase_values": size * 4 * copies * sensors,
                })
    return {"format": "helix-qpsk-repeated-observations-v1", "seed": seed,
            "note": "Each repetition is a fresh independent synthetic observation of the SAME symbol. "
                    "Known chirality +1 and zero phase calibration; different assumptions from "
                    "production observer. Cost rises with repetition count. No security claims.",
            "results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-qpsk-repeated-observations.json"))
    args = parser.parse_args()
    report = benchmark()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
