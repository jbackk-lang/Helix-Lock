"""Reproducible synthetic benchmark for TIMDR M/S vs simple telemetry.

This is an engineering harness, not evidence about real attacks or a commercial
product comparison. It creates labelled benign/anomalous timing traces, fits
thresholds on calibration seeds, and evaluates on disjoint holdout seeds.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Window:
    label: int
    event_count: int
    denied_count: int
    mean_gap: float
    drift: float


def make_window(rng: random.Random, label: int, scenario: str, size: int = 16) -> Window:
    if scenario == "steady":
        gaps = [rng.uniform(0.8, 1.2) for _ in range(size - 1)]
        denied = 0
    elif scenario == "bursty_benign":
        gaps = [rng.uniform(0.08, 0.25) if i % 4 == 0 else rng.uniform(1.0, 2.0)
                for i in range(size - 1)]
        denied = 0
    elif scenario == "denied_burst":
        gaps = [rng.uniform(0.8, 1.2) for _ in range(size - 1)]
        denied = rng.randint(5, 9)
    elif scenario == "rate_burst":
        gaps = [rng.uniform(0.03, 0.12) for _ in range(size - 1)]
        denied = 0
    else:
        raise ValueError(scenario)
    return Window(
        label=label,
        event_count=size,
        denied_count=denied,
        mean_gap=statistics.mean(gaps),
        drift=gaps[-1] - gaps[0],
    )


def dataset(seeds: range) -> list[Window]:
    rows = []
    for seed in seeds:
        rng = random.Random(seed)
        # Equal representation per scenario; seeds are disjoint across splits.
        rows.extend(make_window(rng, 0, "steady") for _ in range(4))
        rows.extend(make_window(rng, 0, "bursty_benign") for _ in range(4))
        rows.extend(make_window(rng, 1, "denied_burst") for _ in range(4))
        rows.extend(make_window(rng, 1, "rate_burst") for _ in range(4))
    return rows


def metrics(rows: list[Window], predictions: list[bool]) -> dict:
    tp = sum(r.label == 1 and p for r, p in zip(rows, predictions))
    fp = sum(r.label == 0 and p for r, p in zip(rows, predictions))
    fn = sum(r.label == 1 and not p for r, p in zip(rows, predictions))
    tn = sum(r.label == 0 and not p for r, p in zip(rows, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(2 * precision * recall / (precision + recall), 4)
        if precision + recall else 0.0,
        "false_positive_rate": round(fp / (fp + tn), 4) if fp + tn else 0.0,
    }


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * q))]


def run() -> dict:
    calibration = dataset(range(1000, 1100))
    holdout = dataset(range(9000, 9100))

    # Baseline B: one transparent rate threshold selected on calibration data.
    rate_threshold = percentile([r.event_count / max(r.mean_gap, 1e-9)
                                  for r in calibration if r.label == 0], 0.95)
    # TIMDR candidate: calibrated threshold over normalized timing drift.
    benign_drift = [abs(r.drift) for r in calibration if r.label == 0]
    drift_threshold = percentile(benign_drift, 0.95)
    # Denied-count is included in the simple telemetry baseline as a second,
    # independently interpretable rule; thresholds are fixed before holdout.
    denied_threshold = 4

    baseline_predictions = [
        (r.event_count / max(r.mean_gap, 1e-9) > rate_threshold)
        or (r.denied_count >= denied_threshold) for r in holdout
    ]
    timdr_predictions = [
        (r.event_count / max(r.mean_gap, 1e-9) > rate_threshold)
        or (abs(r.drift) > drift_threshold)
        or (r.denied_count >= denied_threshold) for r in holdout
    ]

    start = time.perf_counter()
    for r in holdout:
        _ = (r.mean_gap, r.drift, r.event_count)
    feature_runtime = time.perf_counter() - start

    return {
        "status": "synthetic_exploratory_only",
        "calibration_seeds": [1000, 1099],
        "holdout_seeds": [9000, 9099],
        "thresholds": {
            "benign_rate_p95": round(rate_threshold, 6),
            "benign_abs_drift_p95": round(drift_threshold, 6),
            "denied_count": denied_threshold,
        },
        "holdout_windows": len(holdout),
        "simple_telemetry": metrics(holdout, baseline_predictions),
        "timdr_candidate": metrics(holdout, timdr_predictions),
        "feature_loop_seconds": round(feature_runtime, 8),
        "limitations": [
            "synthetic timing distributions only",
            "no real AIRP traces or adversarial validation",
            "labels are scenario labels, not ground-truth attacks",
            "this does not evaluate cryptographic security or EDR products",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
