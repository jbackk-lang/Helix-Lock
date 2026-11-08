"""Matched-data resonance filtering for repeated QPSK observations.

Compare circular mean and a robust trimmed circular estimator on exactly the
same observations. Includes occasional corrupted observation as stress test.
Research only: known chirality +1 and phase reference zero.
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


def decode(observations, method):
    residuals = [p - a for angles, phases in observations for a, p in zip(angles, phases)]
    def mean(values):
        return math.atan2(sum(math.sin(x) for x in values),
                          sum(math.cos(x) for x in values))
    if method == "circular":
        phase = mean(residuals)
    elif method == "resonance":
        # Two-stage robust estimator: pilot direction, trim angular outliers,
        # then re-estimate. It uses no knowledge of the transmitted symbol.
        pilot = mean(residuals)
        distances = sorted((abs(wrap(x - pilot)), i) for i, x in enumerate(residuals))
        keep = max(1, math.ceil(len(residuals) * 0.75))
        phase = mean([residuals[i] for _, i in distances[:keep]])
    else:
        raise ValueError("unknown estimator")
    error, symbol = min((abs(wrap(phase - target)), i)
                        for i, target in enumerate(PHASES))
    return symbol if error <= math.pi / 8 else None


def benchmark(*, sizes=(16, 64, 256), trials=12,
              noise_levels=(0.5, 0.9), repeats=(3, 7),
              corruption_rates=(0, 0.15), seed=20261108):
    rows = []
    for noise in noise_levels:
        for size in sizes:
            for copies in repeats:
                for corruption in corruption_rates:
                    by_method = {name: [] for name in ("circular", "resonance")}
                    for trial in range(trials):
                        rng = random.Random(seed + size * 1009 + trial)
                        payload = rng.randbytes(size)
                        symbols = [(b >> shift) & 3 for b in payload for shift in (6, 4, 2, 0)]
                        observations = []
                        for i, symbol in enumerate(symbols):
                            obs = []
                            for copy in range(copies):
                                angles, phases = transmit(
                                    symbol, 1, sensors=12, noise=noise,
                                    seed=seed + trial * 1000003 + i * 101 + copy)
                                # Matched seeded contamination; an observation
                                # gets an additional random phase shift.
                                crng = random.Random(seed + trial * 3000017 + i * 131 + copy)
                                if crng.random() < corruption:
                                    offset = crng.uniform(-math.pi, math.pi)
                                    phases = [p + offset for p in phases]
                                obs.append((angles, phases))
                            observations.append(obs)
                        for method in by_method:
                            start = time.perf_counter()
                            guesses = [decode(obs, method) for obs in observations]
                            elapsed = time.perf_counter() - start
                            accuracy = sum(g == s for g, s in zip(guesses, symbols)) / len(symbols)
                            by_method[method].append({
                                "accuracy": accuracy,
                                "whole": guesses == symbols,
                                "coverage": sum(g is not None for g in guesses) / len(symbols),
                                "seconds": elapsed,
                            })
                    for method, trials_data in by_method.items():
                        rows.append({
                            "noise": noise, "input_bytes": size,
                            "repeats": copies, "corruption_rate": corruption,
                            "method": method, "trials": trials,
                            "symbol_accuracy": statistics.mean(x["accuracy"] for x in trials_data),
                            "coverage": statistics.mean(x["coverage"] for x in trials_data),
                            "whole_file_success": sum(x["whole"] for x in trials_data) / trials,
                            "estimation_seconds_median": statistics.median(x["seconds"] for x in trials_data),
                        })
    return {"format": "helix-resonance-filter-v1", "seed": seed,
            "note": "Matched synthetic observations. 'Corruption rate' is per repeated observation, "
                    "not per sensor; random common phase offset. Known chirality and reference. "
                    "Timings measure estimation only, excluding signal generation. No AI/security claims.",
            "results": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-resonance-filter.json"))
    args = parser.parse_args()
    result = benchmark()
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
