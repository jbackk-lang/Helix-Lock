"""Synthetic mid-history helix handedness-reversal falsification experiment.

This isolates representation errors when local phase coordinates reverse sign.
It does not claim physical memory asymmetry or spontaneous recovery.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from pathlib import Path
from experiments.helix_chiral_memory_retention import CODEBOOK, wrap, circular_mean, decode_symbol

def run_trial(seed: int, *, cycles: int = 12, flip_after: int = 6,
              start_handedness: int = 1, readout: str = "per_sample",
              disturbance: float = 0.85, measurement_noise: float = 0.08,
              feedback_gain: float = 0.35, recovery_steps: int = 80):
    if cycles < 2 or not 0 <= flip_after <= cycles:
        raise ValueError("require cycles >= 2 and 0 <= flip_after <= cycles")
    if start_handedness not in (-1, 1):
        raise ValueError("start_handedness must be -1 or 1")
    if readout not in ("per_sample", "final_only", "blind", "shuffled_labels"):
        raise ValueError("unknown readout")
    if disturbance < 0 or measurement_noise < 0 or not 0 < feedback_gain <= 1 or recovery_steps < 1:
        raise ValueError("invalid noise, gain or recovery steps")
    rng = random.Random(seed)
    payload = (rng.randrange(4), rng.randrange(4))
    target = tuple(CODEBOOK[i] for i in payload)
    handedness = [start_handedness if i < flip_after else -start_handedness
                  for i in range(cycles)]
    final_h = handedness[-1]
    history = [
        tuple(wrap(h * (target[j] + rng.gauss(0, measurement_noise))) for j in range(2))
        for h in handedness
    ]
    if readout == "per_sample":
        canonical = [tuple(wrap(h * x) for x in sample)
                     for h, sample in zip(handedness, history)]
    elif readout == "shuffled_labels":
        # Negative control: same handedness-label counts but wrong sample alignment.
        labels = list(handedness)
        rng.shuffle(labels)
        canonical = [tuple(wrap(h * x) for x in sample)
                     for h, sample in zip(labels, history)]
    elif readout == "final_only":
        canonical = [tuple(wrap(final_h * x) for x in sample) for sample in history]
    else:
        canonical = history
    reference = tuple(circular_mean([sample[j] for sample in canonical]) for j in range(2))
    current_local = tuple(wrap(final_h * (target[j] + sign * disturbance))
                          for j, sign in enumerate((1, -1)))
    factor = final_h if readout != "blind" else 1
    state = [wrap(factor * x) for x in current_local]
    for _ in range(recovery_steps):
        for j in range(2):
            state[j] = wrap(state[j] - feedback_gain * wrap(state[j] - reference[j]))
    decoded = tuple(decode_symbol(x) for x in state)
    return {
        "seed": seed, "cycles": cycles, "flip_after": flip_after,
        "start_handedness": start_handedness, "readout": readout,
        "payload": list(payload), "decoded": list(decoded),
        "payload_exact_match": decoded == payload,
        "mean_reference_error_rad": round(sum(abs(wrap(reference[j]-target[j])) for j in range(2))/2, 8),
        "mean_final_error_rad": round(sum(abs(wrap(state[j]-target[j])) for j in range(2))/2, 8),
    }

def run(seeds=range(1000, 1100), cycles=12, disturbance=0.85):
    seeds = list(seeds)
    if not seeds:
        raise ValueError("seeds cannot be empty")
    results = {}
    for flip_after in (0, cycles//4, cycles//2, 3*cycles//4, cycles):
        for start_h in (-1, 1):
            for readout in ("per_sample", "final_only", "blind", "shuffled_labels"):
                key = f"flip={flip_after}/start={start_h}/readout={readout}"
                trials = [run_trial(s, cycles=cycles, flip_after=flip_after,
                                    start_handedness=start_h, readout=readout,
                                    disturbance=disturbance) for s in seeds]
                results[key] = {
                    "n": len(trials),
                    "exact_match_rate": round(sum(t["payload_exact_match"] for t in trials)/len(trials), 6),
                    "mean_reference_error_rad": round(sum(t["mean_reference_error_rad"] for t in trials)/len(trials), 8),
                    "mean_final_error_rad": round(sum(t["mean_final_error_rad"] for t in trials)/len(trials), 8),
                }
    return {
        "status": "synthetic_coordinate_reversal_experiment",
        "model": "canonical payload fixed; local phase sign changes at a known history boundary",
        "cycles": cycles, "disturbance_rad": disturbance, "seeds": seeds,
        "results": results,
        "limitations": [
            "a sign reversal is a coordinate-model intervention, not an established physical helix deformation",
            "the per-sample decoder is given the true handedness label of each history sample",
            "shuffled_labels preserves label counts but destroys their alignment to samples",
            "feedback uses an explicitly stored reference and is not spontaneous self-repair",
            "no intrinsic chirality-dependent storage mechanism is included",
        ],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    result = run(range(1000, 1000 + args.seeds))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["results"], indent=2, sort_keys=True))
