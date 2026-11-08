"""Test whether whole-file failures are cumulative errors or memory limits.

All runs use matched deterministic noisy observations. Memory windows are
simple temporal-majority baselines, not trained AI. No cryptographic claims.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
import math
from pathlib import Path
import random
import statistics
import time
import tracemalloc

from experiments.helix_chiral_intelligence import HelixChiralIntelligence, Observation
from experiments.helix_chiral_signal import transmit


def run(*, sizes=(16, 64, 256, 1024), trials=12, noise_levels=(0.12, 0.5),
        windows=(1, 3, 7), seed=20261108, sensors=12):
    if not sizes or not windows or trials < 1 or sensors < 2 or any(n <= 0 for n in sizes):
        raise ValueError("invalid dimensions")
    if any(w < 1 for w in windows) or any(not math.isfinite(n) or n < 0 for n in noise_levels):
        raise ValueError("invalid noise or memory window")
    results = []
    for noise in noise_levels:
        for size in sizes:
            for window in windows:
                trial_rows = []
                for trial in range(trials):
                    rng = random.Random(seed + trial * 1000003 + size * 101)
                    observer = HelixChiralIntelligence(evidence_threshold=0.05)
                    history = deque(maxlen=window)
                    correct = decided = total = 0
                    file_ok = True
                    start = time.perf_counter()
                    tracemalloc.start()
                    for i in range(size):
                        truth = 1  # Constant chirality: isolates noise from reversal latency.
                        a, p = transmit(rng.randrange(4), truth, sensors=sensors,
                                        noise=noise, seed=seed + trial * 1000003 + i)
                        assessment = observer.observe(Observation(float(i), tuple(a), tuple(p)))
                        guess = assessment.handedness
                        if guess is not None:
                            history.append(guess)
                        vote = sum(history)
                        prediction = 1 if vote > 0 else -1 if vote < 0 else None
                        correct += prediction == truth
                        decided += prediction is not None
                        total += 1
                        file_ok &= prediction == truth
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    trial_rows.append({"accuracy": correct / total, "coverage": decided / total,
                                       "whole_file": file_ok, "seconds": time.perf_counter() - start,
                                       "peak_bytes": peak})
                results.append({
                    "noise": noise, "samples": size, "window": window, "trials": trials,
                    "symbol_accuracy": statistics.mean(r["accuracy"] for r in trial_rows),
                    "coverage": statistics.mean(r["coverage"] for r in trial_rows),
                    "whole_sequence_success": sum(r["whole_file"] for r in trial_rows) / trials,
                    "elapsed_seconds_median": statistics.median(r["seconds"] for r in trial_rows),
                    "peak_python_memory_bytes_median": statistics.median(r["peak_bytes"] for r in trial_rows),
                })
    return {"format": "helix-memory-vs-accumulation-v1", "seed": seed,
            "note": "Each sample is one chirality observation, NOT a file byte. "
                    "Constant true chirality, matched deterministic noise per trial; "
                    "window=1 is instantaneous baseline. Python tracemalloc excludes native allocations.",
            "results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-memory-vs-accumulation.json"))
    args = parser.parse_args()
    report = run()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
