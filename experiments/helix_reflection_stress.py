"""Matched delayed-reflection stress test for Helix QPSK estimators.

Echo model: each sensor receives a direct unit phasor plus a delayed,
phase-shifted copy with fixed amplitude; then independent Gaussian phase
noise. Echoes are correlated across repeated observations, not independent
votes. Synthetic only; no physical channel calibration.
"""
from __future__ import annotations

import json
import math
import random

from experiments.helix_chiral_signal import PHASES, transmit
from experiments.helix_resonance_filter import decode as decode_joint
from experiments.helix_phase_coherence import decode_adaptive
from experiments.helix_symbol_consensus import decode_consensus


def reflected_observation(symbol, *, sensors=12, echo_amplitude=0.0,
                          echo_phase=0.0, noise=0.0, seed=0):
    if not 0 <= echo_amplitude < 1:
        raise ValueError("echo amplitude must be in [0,1)")
    if sensors < 1:
        raise ValueError("sensors must be positive")
    rng = random.Random(seed)
    angles = [2 * math.pi * i / sensors for i in range(sensors)]
    base = PHASES[symbol]
    phases = []
    for angle in angles:
        direct = complex(math.cos(base + angle), math.sin(base + angle))
        echo = echo_amplitude * complex(
            math.cos(base + angle + echo_phase),
            math.sin(base + angle + echo_phase))
        received = direct + echo
        phases.append(math.atan2(received.imag, received.real)
                      + rng.gauss(0, noise))
    return angles, phases


def benchmark(*, trials=8, symbols_per_trial=128, copies=(3, 7),
              noise_levels=(0.25, 0.5), echo_amplitudes=(0, 0.45, 0.85),
              echo_phases=(0, math.pi / 2, math.pi), seed=20261108):
    rows = []
    for noise in noise_levels:
        for repeats in copies:
            for amplitude in echo_amplitudes:
                for phase in echo_phases:
                    correct = {m: 0 for m in ("circular", "resonance", "adaptive", "consensus")}
                    accepted = 0
                    count = 0
                    for trial in range(trials):
                        rng = random.Random(seed + trial * 1009)
                        for i in range(symbols_per_trial):
                            symbol = rng.randrange(4)
                            observations = [
                                reflected_observation(
                                    symbol, echo_amplitude=amplitude,
                                    echo_phase=phase, noise=noise,
                                    seed=seed + trial * 1000003 + i * 101 + c)
                                for c in range(repeats)]
                            guesses = {
                                "circular": decode_joint(observations, "circular"),
                                "resonance": decode_joint(observations, "resonance"),
                                "adaptive": decode_adaptive(observations)[0],
                                "consensus": decode_consensus(observations),
                            }
                            for method, guess in guesses.items():
                                correct[method] += guess == symbol
                            accepted += guesses["consensus"] is not None
                            count += 1
                    rows.append({
                        "noise": noise, "repeats": repeats,
                        "echo_amplitude": amplitude, "echo_phase": phase,
                        "symbols": count,
                        "accuracy": {m: correct[m] / count for m in correct},
                        "consensus_coverage": accepted / count,
                    })
    return {"format": "helix-reflection-stress-v1",
            "warning": "Correlated single-tap echo shared by all observations; "
                       "not independent votes. No multipath timing estimation, "
                       "no RF validation, no security claim.",
            "results": rows}


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2))
