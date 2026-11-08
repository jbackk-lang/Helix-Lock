"""Synthetic helical phase signal with angular-array and calibration controls."""
from __future__ import annotations
import argparse
import json
import math
import random
from pathlib import Path

TAU = 2 * math.pi
PHASES = tuple(TAU * j / 4 for j in range(4))

def wrap(x):
    return (x + math.pi) % TAU - math.pi

def transmit(symbol, handedness, *, sensors=12, noise=0.12, seed=0,
             angular_span=TAU, common_phase=0.0):
    if symbol not in range(4) or handedness not in (-1, 1):
        raise ValueError("invalid symbol or handedness")
    if sensors < 1 or noise < 0 or angular_span < 0:
        raise ValueError("invalid sensor geometry or noise")
    rng = random.Random(seed)
    angles = [angular_span * j / sensors for j in range(sensors)]
    phases = [wrap(handedness * theta + PHASES[symbol] + common_phase
                   + rng.gauss(0, noise)) for theta in angles]
    return angles, phases

def decode(angles, phases, *, calibrated_phase=0.0):
    if not angles or len(angles) != len(phases):
        raise ValueError("angles and phases must be nonempty and aligned")
    scores = []
    for h in (-1, 1):
        for symbol in range(4):
            expected = PHASES[symbol] + calibrated_phase
            score = sum(math.cos(wrap(p - h*a - expected))
                        for a, p in zip(angles, phases))
            scores.append((score, h, symbol))
    scores.sort(reverse=True)
    return {"handedness": scores[0][1], "symbol": scores[0][2],
            "score_margin": round(scores[0][0] - scores[1][0], 8)}

def trial(seed, *, sensors=12, noise=0.12, angular_span=TAU,
          common_phase=0.0, calibrated_phase=0.0):
    rng = random.Random(seed)
    symbol = rng.randrange(4)
    handedness = rng.choice((-1, 1))
    angles, phases = transmit(symbol, handedness, sensors=sensors,
                              noise=noise, seed=seed+100000,
                              angular_span=angular_span,
                              common_phase=common_phase)
    found = decode(angles, phases, calibrated_phase=calibrated_phase)
    return {"symbol": symbol, "handedness": handedness,
            "symbol_correct": found["symbol"] == symbol,
            "handedness_correct": found["handedness"] == handedness,
            "both_correct": found["symbol"] == symbol and found["handedness"] == handedness,
            "score_margin": found["score_margin"]}

def run(seeds=range(1000, 1200)):
    seeds = list(seeds)
    if not seeds:
        raise ValueError("empty seeds")
    results = {}
    for sensors, span in ((1, TAU), (2, TAU), (4, TAU), (12, TAU), (12, TAU/8)):
        for noise in (0.0, 0.12, 0.4):
            for common, calibrated in ((0.0, 0.0), (math.pi/2, 0.0), (math.pi/2, math.pi/2)):
                key = (f"sensors={sensors}/span={span:.6f}/noise={noise}/"
                       f"offset={common:.3f}/calibrated={calibrated:.3f}")
                rows = [trial(seed, sensors=sensors, noise=noise,
                              angular_span=span, common_phase=common,
                              calibrated_phase=calibrated) for seed in seeds]
                results[key] = {"n": len(rows),
                                "payload_accuracy": round(sum(r["symbol_correct"] for r in rows)/len(rows), 6),
                                "chirality_accuracy": round(sum(r["handedness_correct"] for r in rows)/len(rows), 6),
                                "joint_accuracy": round(sum(r["both_correct"] for r in rows)/len(rows), 6),
                                "mean_score_margin": round(sum(r["score_margin"] for r in rows)/len(rows), 8)}
    return {"status": "synthetic_helical_phase_signal", "seeds": seeds, "results": results,
            "limitations": [
                "Spatial phase pattern, not evidence all signals propagate as helices.",
                "Absolute payload phase requires a calibrated reference.",
                "A single angular receiver cannot distinguish +/- handedness.",
                "Ideal angular sensors; no multipath or dispersion.",
            ]}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    p.add_argument("--seeds", type=int, default=200)
    args = p.parse_args()
    result = run(range(1000, 1000 + args.seeds))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["results"], indent=2, sort_keys=True))
