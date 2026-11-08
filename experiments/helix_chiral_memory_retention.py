"""Synthetic factorial test of helix handedness and phase-memory retention."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path

CODEBOOK = (-1.2, -0.4, 0.4, 1.2)
MODES = ("no_history", "last_transition", "full_cycle_history")

def wrap(x):
    return (x + math.pi) % (2.0 * math.pi) - math.pi

def circular_mean(values):
    return math.atan2(sum(math.sin(x) for x in values), sum(math.cos(x) for x in values))

def decode_symbol(angle):
    return min(range(4), key=lambda i: abs(wrap(angle - CODEBOOK[i])))

def run_trial(seed, *, handedness, mode, orientation_aware=True, disturbance=0.85,
              history_cycles=12, feedback_gain=0.35, recovery_steps=80,
              measurement_noise=0.08, process_noise=0.002):
    if handedness not in (-1, 1):
        raise ValueError("handedness must be -1 (left) or +1 (right)")
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    if history_cycles < 1 or recovery_steps < 1:
        raise ValueError("history_cycles and recovery_steps must be positive")
    if min(disturbance, measurement_noise, process_noise) < 0:
        raise ValueError("noise and disturbance magnitudes must be non-negative")
    if not 0 < feedback_gain <= 1:
        raise ValueError("feedback_gain must be in (0, 1]")
    rng = random.Random(seed)
    payload = (rng.randrange(4), rng.randrange(4))
    target = (CODEBOOK[payload[0]], CODEBOOK[payload[1]])
    history = []
    for _ in range(history_cycles):
        noise = (rng.gauss(0, measurement_noise), rng.gauss(0, measurement_noise))
        history.append(tuple(wrap(handedness * (target[j] + noise[j])) for j in range(2)))
    if mode == "last_transition":
        stored = history[-1]
    elif mode == "full_cycle_history":
        stored = tuple(circular_mean([sample[j] for sample in history]) for j in range(2))
    else:
        stored = None
    current = []
    for j, sign in enumerate((1.0, -1.0)):
        noise = rng.gauss(0, measurement_noise)
        current.append(wrap(handedness * (target[j] + sign * disturbance + noise)))
    factor = handedness if orientation_aware else 1
    state = [wrap(factor * x) for x in current]
    reference = None if stored is None else tuple(wrap(factor * x) for x in stored)
    ref_error = None if reference is None else sum(abs(wrap(reference[j]-target[j])) for j in range(2))/2
    if reference is not None:
        for _ in range(recovery_steps):
            for j in range(2):
                state[j] = wrap(state[j] - feedback_gain * wrap(state[j]-reference[j])
                                + rng.gauss(0, process_noise))
    decoded = tuple(decode_symbol(x) for x in state)
    return {
        "seed": seed, "handedness": "right" if handedness == 1 else "left",
        "mode": mode, "orientation_aware": orientation_aware,
        "payload": list(payload), "decoded": list(decoded),
        "payload_exact_match": decoded == payload,
        "reference_error_rad": None if ref_error is None else round(ref_error, 8),
        "final_phase_error_rad": round(sum(abs(wrap(state[j]-target[j])) for j in range(2))/2, 8),
        "disturbance_rad": disturbance,
    }

def run(seeds=range(1000, 1100), disturbances=(0.25, 0.5, 0.85, 1.2), history_cycles=12):
    seeds = list(seeds)
    if not seeds:
        raise ValueError("at least one seed is required")
    rows, summary = {}, {}
    for d in disturbances:
        for h in (-1, 1):
            for aware in (False, True):
                for mode in MODES:
                    key = f"{'right' if h == 1 else 'left'}/{'aware' if aware else 'blind'}/{mode}/d={d:g}"
                    trials = [run_trial(s, handedness=h, mode=mode, orientation_aware=aware,
                                        disturbance=d, history_cycles=history_cycles) for s in seeds]
                    rows[key] = trials
                    refs = [x["reference_error_rad"] for x in trials if x["reference_error_rad"] is not None]
                    summary[key] = {
                        "trials": len(trials),
                        "payload_exact_match_rate": round(sum(x["payload_exact_match"] for x in trials)/len(trials), 6),
                        "mean_final_phase_error_rad": round(sum(x["final_phase_error_rad"] for x in trials)/len(trials), 8),
                        "mean_reference_error_rad": None if not refs else round(sum(refs)/len(refs), 8),
                    }
    return {
        "status": "synthetic_factorial_experiment_only",
        "question": "Does handedness change memory retention after separating mirror-coordinate convention from memory quality?",
        "model": "local_phase = handedness * canonical_phase; finite noisy history; optional explicit reference feedback",
        "codebook_rad": list(CODEBOOK), "modes": list(MODES),
        "orientation_aware_definition": "multiply local phase by handedness before storing/reading canonical information",
        "history_cycles": history_cycles, "seeds": seeds, "disturbances_rad": list(disturbances),
        "summary": summary, "trials": rows,
        "interpretation_limits": [
            "synthetic phase-memory toy model, not production Helix-Lock, GIA-TIMDR, or TSI",
            "orientation normalization is a coordinate convention, not a physical law",
            "reference feedback is imposed by this experiment, not derived from Chronoprocess",
            "payload is a two-symbol phase code, not arbitrary data or ciphertext",
            "a blind left/right gap indicates coordinate mismatch, not necessarily intrinsic memory asymmetry",
            "intrinsic chirality dependence requires a justified handedness-dependent storage/noise mechanism",
        ],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    result = run(range(1000, 1000 + args.seeds))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
