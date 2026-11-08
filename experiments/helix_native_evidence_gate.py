"""Evidence gate for Helix Native history experiments.

Never label an observed gain 'proven': this is a deterministic synthetic
benchmark, not a statistically independent validation.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from experiments.helix_native_history_comparison import compare


def evaluate(report: dict, *, min_gain: float = 0.02,
             max_extra_reversal_delay: int = 2) -> dict:
    metrics = report["metrics"]
    instant = metrics["instant"]
    history = metrics["history"]
    gain = history["accuracy_with_abstentions"] - instant["accuracy_with_abstentions"]
    coverage_change = history["coverage"] - instant["coverage"]
    a = instant["reversal_delays"]
    b = history["reversal_delays"]
    if len(a) != len(b) or not a:
        raise ValueError("matched reversal trials required")
    if not all(isinstance(x, (int, type(None))) for x in a + b):
        raise ValueError("invalid reversal delay")
    # No response is an explicit failure, not silently excluded from latency.
    misses = sum(x is None for x in b)
    baseline_misses = sum(x is None for x in a)
    paired = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    extra_delays = [y - x for x, y in paired]
    worst_extra_delay = max(extra_delays) if extra_delays else None
    if not all(math.isfinite(v) for v in (gain, coverage_change)):
        raise ValueError("nonfinite metrics")
    qualifies = (gain >= min_gain and coverage_change >= 0 and
                 misses <= baseline_misses and
                 worst_extra_delay is not None and
                 worst_extra_delay <= max_extra_reversal_delay)
    if qualifies:
        verdict = "candidate_gain_not_proof"
    elif gain < 0 or coverage_change < 0 or misses > baseline_misses or (
            worst_extra_delay is not None and
            worst_extra_delay > max_extra_reversal_delay):
        verdict = "tradeoff_or_regression"
    else:
        verdict = "inconclusive"
    return {"verdict": verdict, "gain": gain, "coverage_change": coverage_change,
            "history_missed_reversals": misses,
            "instant_missed_reversals": baseline_misses,
            "worst_extra_reversal_delay": worst_extra_delay,
            "paired_reversal_trials": len(paired),
            "thresholds": {"min_gain": min_gain,
                           "max_extra_reversal_delay": max_extra_reversal_delay},
            "warning": "Heuristic gate on synthetic data; not proof of generalization or security."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-native-evidence-gate.json"))
    args = parser.parse_args()
    # Evaluate distinct regimes rather than selecting a favorable result.
    regimes = [
        {"name": "noiseless", "noise": 0.0},
        {"name": "moderate_noise", "noise": 0.7},
        {"name": "strong_noise", "noise": 1.4},
    ]
    output = {"format": "helix-native-evidence-gate-v0", "regimes": []}
    for regime in regimes:
        result = compare(noise=regime["noise"])
        output["regimes"].append({
            "name": regime["name"], "parameters": result["parameters"],
            "metrics": result["metrics"], "assessment": evaluate(result)})
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
