"""Matched-data comparison of instantaneous and temporal chirality estimates.

Temporal majority is a simple baseline, NOT learned intelligence. Its latency
on reversals is measured to avoid reporting only a noise benefit.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
import random
from pathlib import Path

from experiments.helix_chiral_intelligence import HelixChiralIntelligence, Observation
from experiments.helix_chiral_signal import transmit


def compare(*, seeds=range(12), samples=24, window=5, noise=0.7,
            sensors=6, angular_span=3.141592653589793):
    if samples < 2 or window < 1 or sensors < 2 or noise < 0:
        raise ValueError("invalid comparison parameters")
    counts = {"instant_correct": 0, "instant_decided": 0,
              "history_correct": 0, "history_decided": 0,
              "total": 0, "instant_reversal_delay": [],
              "history_reversal_delay": []}
    for seed in seeds:
        rng = random.Random(seed)
        observer = HelixChiralIntelligence(evidence_threshold=0.05)
        history = deque(maxlen=window)
        instant_trace = []
        smooth_trace = []
        midpoint = samples // 2
        for t in range(samples):
            truth = 1 if t < midpoint else -1
            a, p = transmit(rng.randrange(4), truth, sensors=sensors, noise=noise,
                            seed=seed * 10000 + t, angular_span=angular_span)
            result = observer.observe(Observation(float(t), tuple(a), tuple(p)))
            instant = result.handedness
            if instant is not None:
                history.append(instant)
            votes = sum(history)
            smooth = (1 if votes > 0 else -1 if votes < 0 else None)
            instant_trace.append(instant)
            smooth_trace.append(smooth)
            counts["total"] += 1
            for name, guess in (("instant", instant), ("history", smooth)):
                counts[name + "_decided"] += guess is not None
                counts[name + "_correct"] += guess == truth
        for name, trace in (("instant", instant_trace), ("history", smooth_trace)):
            first = next((i for i in range(midpoint, samples) if trace[i] == -1), None)
            counts[name + "_reversal_delay"].append(
                None if first is None else first - midpoint)
    total = counts["total"]
    return {"format": "helix-native-history-comparison-v0",
            "parameters": {"seeds": list(seeds), "samples": samples,
                           "window": window, "noise": noise, "sensors": sensors,
                           "angular_span": angular_span},
            "metrics": {name: {
                "accuracy_with_abstentions": counts[name + "_correct"] / total,
                "coverage": counts[name + "_decided"] / total,
                "reversal_delays": counts[name + "_reversal_delay"]}
                for name in ("instant", "history")},
            "note": "Temporal majority is a baseline; reversal delays are measured. No security claims."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-native-history-comparison.json"))
    args = parser.parse_args()
    report = compare()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
