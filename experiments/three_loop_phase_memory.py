"""Synthetic three-loop phase-recovery experiment.

This is an explanatory dynamical toy model, not the production Chronoprocess,
not TSI, and not a cryptographic self-repair mechanism.
"""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path

def wrap(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi

def run_trial(seed: int, *, mode: str, steps: int = 900, disturbance_start: int = 250, disturbance_end: int = 400) -> dict:
    rng = random.Random(seed)
    dt = 0.02
    omega = [1.0, 1.0, 1.0]
    theta = [0.0, 0.7, -0.45]
    # The stored signature is the stable pre-disturbance relative phase pattern.
    reference = [wrap(theta[1] - theta[0]), wrap(theta[2] - theta[0])]
    coupling = 0.0 if mode == "no_memory_no_coupling" else 0.18
    memory_gain = 0.0 if mode != "coupling_plus_memory" else 0.10
    errors = []
    for step in range(steps):
        disturbance = 0.0
        if disturbance_start <= step < disturbance_end:
            disturbance = 0.85
        phase_errors = [wrap(theta[1] - theta[0] - reference[0]), wrap(theta[2] - theta[0] - reference[1])]
        # Symmetric nearest-neighbour coupling is a candidate phase model.
        coupling_terms = [
            math.sin(theta[1] - theta[0]) + math.sin(theta[2] - theta[0]),
            math.sin(theta[0] - theta[1]) + math.sin(theta[2] - theta[1]),
            math.sin(theta[0] - theta[2]) + math.sin(theta[1] - theta[2]),
        ]
        correction = [0.0, 0.0, 0.0]
        if memory_gain:
            correction[1] = -memory_gain * phase_errors[0]
            correction[2] = -memory_gain * phase_errors[1]
        noise = [rng.uniform(-0.002, 0.002) for _ in range(3)]
        velocity = [
            omega[i] + coupling * coupling_terms[i] + correction[i] + noise[i]
            for i in range(3)
        ]
        velocity[2] += disturbance
        theta = [theta[i] + dt * velocity[i] for i in range(3)]
        if step >= disturbance_end:
            e1 = wrap(theta[1] - theta[0] - reference[0])
            e2 = wrap(theta[2] - theta[0] - reference[1])
            errors.append((abs(e1) + abs(e2)) / 2.0)
    return {
        "seed": seed, "mode": mode,
        "post_disturbance_mean_phase_error": round(sum(errors) / len(errors), 8),
        "post_disturbance_final_phase_error": round(errors[-1], 8),
        "reference_relative_phases": [round(x, 8) for x in reference],
        "disturbance_steps": disturbance_end - disturbance_start,
    }

def run(seeds=range(100, 200)) -> dict:
    modes = ("no_memory_no_coupling", "coupling_only", "coupling_plus_memory")
    rows = {mode: [run_trial(seed, mode=mode) for seed in seeds] for mode in modes}
    means = {mode: round(sum(x["post_disturbance_mean_phase_error"] for x in values) / len(values), 8) for mode, values in rows.items()}
    return {
        "status": "synthetic_dynamical_toy_model_only",
        "model": "three_phase_oscillators_with_temporary_frequency_disturbance",
        "seeds": [100, 199],
        "trial_count_per_mode": len(rows[modes[0]]),
        "mean_post_disturbance_phase_error": means,
        "trials": rows,
        "interpretation_limits": [
            "not the production TIMDR Chronoprocess or TSI implementation",
            "memory stores a pre-disturbance relative-phase reference; it does not store or reconstruct payload data",
            "the memory feedback law is an explicit added control rule, not an emergent property",
            "phase recovery is not cryptographic integrity or data recovery",
        ],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output: args.output.write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k != "trials"}, indent=2, sort_keys=True))