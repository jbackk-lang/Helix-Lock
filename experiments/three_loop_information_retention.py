"""Three-loop experiment separating phase coherence from encoded-information retention.

This is an explicit synthetic model, not production TIMDR/TSI or a claim of
cryptographic self-repair. The payload is represented by two relative phases.
"""
from __future__ import annotations
import json, math, random
from pathlib import Path

CODEBOOK = (-1.2, -0.4, 0.4, 1.2)
MODES = ("no_history", "last_transition", "full_cycle_history")

def wrap(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi

def circular_mean(values: list[float]) -> float:
    return math.atan2(sum(math.sin(v) for v in values), sum(math.cos(v) for v in values))

def decode_symbol(angle: float) -> int:
    return min(range(len(CODEBOOK)), key=lambda i: abs(wrap(angle - CODEBOOK[i])))

def run_trial(seed: int, *, mode: str, amplitude: float = 0.85, duration: int = 80,
              disturbance_targets: tuple[int, ...] = (2,), steps_after: int = 500,
              history_cycles: int = 12, feedback_gain: float = 1.8) -> dict:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    if duration < 1 or steps_after < 1 or history_cycles < 1:
        raise ValueError("duration, steps_after and history_cycles must be positive")
    if any(i not in (0, 1, 2) for i in disturbance_targets):
        raise ValueError("disturbance targets must be loop indices 0, 1, or 2")
    rng = random.Random(seed)
    dt = 0.02
    payload = (rng.randrange(4), rng.randrange(4))
    target = [CODEBOOK[payload[0]], CODEBOOK[payload[1]]]
    theta = [0.0, target[0], target[1]]
    omega = [1.0, 1.0, 1.0]
    # Observe the complete three-loop state once per full 3-step cycle.
    history: list[tuple[float, float]] = []
    pre_steps = history_cycles * 3
    for step in range(pre_steps):
        theta = [theta[i] + dt * omega[i] + rng.uniform(-0.0001, 0.0001) for i in range(3)]
        if (step + 1) % 3 == 0:
            history.append((
                wrap(theta[1] - theta[0] + rng.uniform(-0.01, 0.01)),
                wrap(theta[2] - theta[0] + rng.uniform(-0.01, 0.01)),
            ))
    if mode == "last_transition":
        reference = history[-1]
    elif mode == "full_cycle_history":
        reference = (
            circular_mean([x[0] for x in history]),
            circular_mean([x[1] for x in history]),
        )
    else:
        reference = None
    errors = []
    coherence_samples = []
    total_steps = duration + steps_after
    for step in range(total_steps):
        disturbed = step < duration
        velocities = list(omega)
        if disturbed:
            for index in disturbance_targets:
                velocities[index] += amplitude
        if reference is not None and not disturbed:
            e1 = wrap(theta[1] - theta[0] - reference[0])
            e2 = wrap(theta[2] - theta[0] - reference[1])
            # Explicit reference-feedback law; not an emergent Chronoprocess property.
            velocities[1] += -feedback_gain * e1
            velocities[2] += -feedback_gain * e2
        theta = [theta[i] + dt * velocities[i] + rng.uniform(-0.0001, 0.0001) for i in range(3)]
        if step >= duration:
            e1 = wrap(theta[1] - theta[0] - target[0])
            e2 = wrap(theta[2] - theta[0] - target[1])
            errors.append((abs(e1) + abs(e2)) / 2.0)
            coherence_samples.append(abs(sum(complex(math.cos(x), math.sin(x)) for x in theta)) / 3.0)
    final_relative = (wrap(theta[1] - theta[0]), wrap(theta[2] - theta[0]))
    decoded = (decode_symbol(final_relative[0]), decode_symbol(final_relative[1]))
    return {
        "seed": seed, "mode": mode, "amplitude": amplitude, "duration": duration,
        "disturbance_targets": list(disturbance_targets),
        "mean_post_phase_error_rad": round(sum(errors) / len(errors), 8),
        "final_phase_error_rad": round(errors[-1], 8),
        "mean_order_parameter": round(sum(coherence_samples) / len(coherence_samples), 8),
        "payload_symbols": list(payload), "decoded_symbols": list(decoded),
        "payload_exact_match": decoded == payload,
        "reference_error_rad": None if reference is None else round((abs(wrap(reference[0]-target[0]))+abs(wrap(reference[1]-target[1])))/2, 8),
    }

def run(seeds=range(1000, 1100), amplitudes=(0.1, 0.25, 0.5, 0.85, 1.2, 1.8, 2.5)) -> dict:
    seed_list = list(seeds)
    if not seed_list:
        raise ValueError("at least one seed is required")
    rows = {}
    summary = {}
    for amplitude in amplitudes:
        for mode in MODES:
            key = f"{mode}@{amplitude:g}"
            trials = [run_trial(seed, mode=mode, amplitude=amplitude) for seed in seed_list]
            rows[key] = trials
            errors = sorted(x["mean_post_phase_error_rad"] for x in trials)
            summary[key] = {
                "trials": len(trials),
                "mean_phase_error_rad": round(sum(errors)/len(errors), 8),
                "median_phase_error_rad": round(errors[len(errors)//2], 8),
                "p90_phase_error_rad": round(errors[min(len(errors)-1, math.ceil(0.9*len(errors))-1)], 8),
                "payload_exact_match_rate": round(sum(x["payload_exact_match"] for x in trials)/len(trials), 8),
                "mean_order_parameter": round(sum(x["mean_order_parameter"] for x in trials)/len(trials), 8),
            }
    return {
        "status": "synthetic_experiment_only",
        "question": "Does full-cycle history preserve encoded relative-phase information better than one-transition memory or no history?",
        "payload_encoding": "two 2-bit symbols encoded in relative phases from a four-angle codebook",
        "history_definition": "one observation per complete three-step cycle; last_transition uses one sample, full_cycle_history uses circular mean of the configured history window",
        "seeds": seed_list, "amplitudes": list(amplitudes),
        "duration_steps": 80, "post_disturbance_steps": 500,
        "summary": summary, "trials": rows,
        "interpretation_limits": [
            "explicit toy model, not production TIMDR, TSI, or Helix-Lock dynamics",
            "feedback law is added by the experiment; it is not derived from the original Chronoprocess",
            "phase coherence/order parameter is not equivalent to payload recovery",
            "payload is a small phase code, not ciphertext or arbitrary file data",
            "results cannot establish cryptographic integrity, attack resistance, or self-repair in production",
        ],
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
