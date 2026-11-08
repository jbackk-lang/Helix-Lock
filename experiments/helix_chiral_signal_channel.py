"""Synthetic angular-array chirality channel with motion and coherent reflection.

A shared Doppler phase is indistinguishable from an unknown payload phase at one
instant. A known pilot reference permits calibration. Reflections can alter
angular winding and should not be treated as evidence of intrinsic handedness.
"""
import argparse
import json
import math
import random

from experiments.helix_chiral_signal import PHASES, TAU, decode, wrap


def channel(symbol, handedness, *, sensors=12, noise=0.12, seed=0,
            doppler_phase=0.0, reflection_gain=0.0,
            reflection_handedness=None):
    if symbol not in range(4) or handedness not in (-1, 1):
        raise ValueError("invalid signal")
    if sensors < 1 or noise < 0 or reflection_gain < 0:
        raise ValueError("invalid channel")
    rng = random.Random(seed)
    angles = [TAU * j / sensors for j in range(sensors)]
    if reflection_handedness is None:
        reflection_handedness = -handedness
    if reflection_handedness not in (-1, 1):
        raise ValueError("invalid reflected winding")
    phases = []
    for theta in angles:
        direct = handedness * theta + PHASES[symbol] + doppler_phase
        echo = reflection_handedness * theta + PHASES[symbol] + doppler_phase
        re = math.cos(direct) + reflection_gain * math.cos(echo)
        im = math.sin(direct) + reflection_gain * math.sin(echo)
        phases.append(wrap(math.atan2(im, re) + rng.gauss(0, noise)))
    return angles, phases


def trial(seed, *, sensors=12, noise=0.12, doppler_phase=0.0,
          reflection_gain=0.0, calibrated_phase=0.0):
    rng = random.Random(seed)
    symbol = rng.randrange(4)
    handedness = rng.choice((-1, 1))
    angles, phases = channel(symbol, handedness, sensors=sensors,
                             noise=noise, seed=seed + 200000,
                             doppler_phase=doppler_phase,
                             reflection_gain=reflection_gain)
    result = decode(angles, phases, calibrated_phase=calibrated_phase)
    return (result["symbol"] == symbol, result["handedness"] == handedness)


def run(seeds=range(1000, 1200)):
    seeds = list(seeds)
    if not seeds:
        raise ValueError("empty seeds")
    results = {}
    for doppler in (0.0, math.pi / 2):
        for gain in (0.0, 0.3, 0.8, 1.2):
            for calibrated in (0.0, doppler):
                key = f"doppler={doppler:.6f}/echo={gain}/calibration={calibrated:.6f}"
                rows = [trial(seed, doppler_phase=doppler,
                              reflection_gain=gain, calibrated_phase=calibrated)
                        for seed in seeds]
                results[key] = {
                    "n": len(rows),
                    "payload_accuracy": round(sum(x for x, _ in rows) / len(rows), 6),
                    "chirality_accuracy": round(sum(y for _, y in rows) / len(rows), 6),
                    "joint_accuracy": round(sum(x and y for x, y in rows) / len(rows), 6)}
    return {"model": "synthetic angular phase channel", "results": results,
            "limitations": ["Doppler is modeled as a phase offset at one snapshot, not a full frequency-time channel.",
                            "Echo is a coherent opposite-winding component, not a geometric ray-tracing model."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    if args.output:
        with open(args.output, "w", encoding="utf-8") as out:
            json.dump(result, out, indent=2, sort_keys=True)
    print(json.dumps(result["results"], indent=2, sort_keys=True))
