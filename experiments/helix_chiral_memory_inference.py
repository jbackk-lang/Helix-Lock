"""Infer helix handedness changes from noisy local phases without per-sample labels.

Only the first handedness sign is optionally anchored. The unanchored problem
has an exact global sign ambiguity under the symmetric phase codebook.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from pathlib import Path
from experiments.helix_chiral_memory_retention import CODEBOOK, wrap, circular_mean, decode_symbol

def infer_labels(samples, *, initial_handedness=1, flip_penalty=0.15):
    """Viterbi path minimizing canonical phase discontinuity and switch penalty.

    Returns one of the two globally mirror-equivalent solutions if unanchored.
    """
    if not samples or any(len(x) != 2 for x in samples):
        raise ValueError("samples must be a nonempty sequence of phase pairs")
    if initial_handedness not in (-1, 1, None):
        raise ValueError("initial_handedness must be -1, 1 or None")
    if flip_penalty < 0:
        raise ValueError("flip_penalty must be nonnegative")
    states = (-1, 1)
    costs = {h: (0.0 if initial_handedness is None or h == initial_handedness
                  else float("inf")) for h in states}
    back = []
    for t in range(1, len(samples)):
        next_costs, prevs = {}, {}
        for h in states:
            options = []
            for prev_h in states:
                jump = sum(wrap(h * samples[t][j] - prev_h * samples[t-1][j])**2
                           for j in range(2))
                options.append((costs[prev_h] + jump + (flip_penalty if h != prev_h else 0),
                                prev_h))
            next_costs[h], prevs[h] = min(options)
        costs = next_costs
        back.append(prevs)
    last = min(states, key=lambda h: costs[h])
    labels = [last]
    for prevs in reversed(back):
        last = prevs[last]
        labels.append(last)
    labels.reverse()
    return labels

def trial(seed, *, cycles=12, flip_after=6, initial_handedness=1,
          anchored=True, measurement_noise=0.08, flip_penalty=0.15):
    if cycles < 2 or not 0 <= flip_after <= cycles:
        raise ValueError("invalid cycle count or flip boundary")
    if initial_handedness not in (-1, 1) or measurement_noise < 0:
        raise ValueError("invalid handedness or noise")
    rng = random.Random(seed)
    payload = (rng.randrange(4), rng.randrange(4))
    target = [CODEBOOK[i] for i in payload]
    actual = [initial_handedness if t < flip_after else -initial_handedness
              for t in range(cycles)]
    samples = [tuple(wrap(h * (target[j] + rng.gauss(0, measurement_noise)))
                     for j in range(2)) for h in actual]
    # The initial sign is genuinely unknown when flip_after=0; the anchor
    # represents a measured sign at the FIRST sample, not the pre-flip sign.
    anchor = actual[0] if anchored else None
    inferred = infer_labels(samples, initial_handedness=anchor, flip_penalty=flip_penalty)
    canonical = [tuple(wrap(h * x) for x in sample)
                 for h, sample in zip(inferred, samples)]
    reference = [circular_mean([row[j] for row in canonical]) for j in range(2)]
    decoded = tuple(decode_symbol(x) for x in reference)
    correct = sum(x == y for x, y in zip(inferred, actual))
    # Global sign ambiguity is a symmetry, not necessarily an inference failure.
    modulo_global = max(correct, cycles - correct) / cycles
    return {
        "seed": seed, "flip_after": flip_after, "anchored": anchored,
        "actual": actual, "inferred": inferred,
        "label_accuracy": correct/cycles,
        "label_accuracy_mod_global_sign": modulo_global,
        "payload_exact_match": decoded == payload,
        "phase_error_rad": sum(abs(wrap(reference[j]-target[j])) for j in range(2))/2,
    }

def run(seeds=range(1000, 1100), cycles=12, noise_levels=(0.08, 0.2, 0.4)):
    seeds = list(seeds)
    if not seeds:
        raise ValueError("seeds must be nonempty")
    summary = {}
    for noise in noise_levels:
        for flip_after in (0, cycles//4, cycles//2, 3*cycles//4, cycles):
            for anchored in (True, False):
                key = f"noise={noise:g}/flip={flip_after}/anchored={anchored}"
                rows = [trial(s, cycles=cycles, flip_after=flip_after,
                              anchored=anchored, measurement_noise=noise) for s in seeds]
                summary[key] = {
                    "n": len(rows),
                    "payload_exact_match_rate": round(sum(x["payload_exact_match"] for x in rows)/len(rows), 6),
                    "mean_label_accuracy": round(sum(x["label_accuracy"] for x in rows)/len(rows), 6),
                    "mean_label_accuracy_mod_global_sign": round(
                        sum(x["label_accuracy_mod_global_sign"] for x in rows)/len(rows), 6),
                    "mean_phase_error_rad": round(sum(x["phase_error_rad"] for x in rows)/len(rows), 8),
                }
    return {
        "status": "synthetic_inference_no_per_sample_oracle",
        "method": "two-state Viterbi with phase-continuity cost and switch penalty",
        "known": "two stable canonical phase symbols; optional first-sample handedness anchor",
        "not_known": "handedness of each subsequent sample; reversal boundary",
        "seeds": seeds, "cycles": cycles, "summary": summary,
        "limitations": [
            "canonical phases are assumed constant through the history",
            "the phase codebook is symmetric under sign, so absolute handedness and payload are not identifiable without an anchor",
            "the unanchored solver's global sign choice is arbitrary; modulo-global-sign accuracy is reported separately",
            "this does not infer physical torsion from measured 3D geometry",
            "no production G5 or TSI behavior is validated",
        ],
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    p.add_argument("--seeds", type=int, default=100)
    args = p.parse_args()
    result = run(range(1000, 1000 + args.seeds))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
