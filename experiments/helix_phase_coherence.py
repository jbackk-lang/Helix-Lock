"""Phase-coherence adaptive estimator for repeated QPSK observations.

Research-only estimator. Uses agreement between observation-level phasors
to choose circular averaging or a robust estimator. No crypto or replay claims.
"""
from __future__ import annotations

import math

from experiments.helix_resonance_filter import decode as baseline_decode
from experiments.helix_chiral_signal import PHASES, wrap


def coherence(observations):
    if not observations:
        raise ValueError("at least one observation required")
    vectors = []
    for angles, phases in observations:
        if not angles or len(angles) != len(phases):
            raise ValueError("invalid sensor observation")
        residuals = [phase - angle for angle, phase in zip(angles, phases)]
        vector = complex(sum(math.cos(x) for x in residuals),
                         sum(math.sin(x) for x in residuals))
        if abs(vector) > 0:
            vectors.append(vector / abs(vector))
    if not vectors:
        return 0.0
    return abs(sum(vectors)) / len(vectors)


def decode_adaptive(observations, *, coherence_threshold=0.85):
    if not 0 <= coherence_threshold <= 1:
        raise ValueError("coherence threshold must be in [0,1]")
    # Conservative clean-path default: no robust filtering when copies agree.
    score = coherence(observations)
    method = "circular" if score >= coherence_threshold else "resonance"
    return baseline_decode(observations, method), method, score


def benchmark(*, sizes=(16, 64), trials=6, noise_levels=(0.5, 0.9),
              repeats=(3, 7), corruption_rates=(0.0, 0.15),
              threshold=0.85, seed=20261108):
    import random
    from experiments.helix_chiral_signal import transmit
    rows = []
    for noise in noise_levels:
        for size in sizes:
            for copies in repeats:
                for corruption in corruption_rates:
                    totals = {name: 0 for name in ("circular", "resonance", "adaptive")}
                    selected_robust = 0
                    count = 0
                    for trial in range(trials):
                        rng = random.Random(seed + trial + size * 1009)
                        payload = rng.randbytes(size)
                        symbols = [(b >> shift) & 3 for b in payload for shift in (6, 4, 2, 0)]
                        for i, symbol in enumerate(symbols):
                            observations = []
                            for copy in range(copies):
                                angles, phases = transmit(
                                    symbol, 1, sensors=12, noise=noise,
                                    seed=seed + trial * 1000003 + i * 101 + copy)
                                crng = random.Random(seed + trial * 3000017 + i * 131 + copy)
                                if crng.random() < corruption:
                                    offset = crng.uniform(-math.pi, math.pi)
                                    phases = [p + offset for p in phases]
                                observations.append((angles, phases))
                            for method in ("circular", "resonance"):
                                totals[method] += baseline_decode(observations, method) == symbol
                            guess, selected, _ = decode_adaptive(
                                observations, coherence_threshold=threshold)
                            totals["adaptive"] += guess == symbol
                            selected_robust += selected == "resonance"
                            count += 1
                    rows.append({
                        "noise": noise, "input_bytes": size, "repeats": copies,
                        "corruption_rate": corruption, "symbols": count,
                        "coherence_threshold": threshold,
                        "symbol_accuracy": {name: totals[name] / count for name in totals},
                        "robust_selection_fraction": selected_robust / count,
                    })
    return {"format": "helix-phase-coherence-v1", "seed": seed,
            "note": "Synthetic matched QPSK observations, no channel echoes modeled; "
                    "coherence is a decoding heuristic, NOT authentication.",
            "results": rows}


if __name__ == "__main__":
    import json
    print(json.dumps(benchmark(), indent=2))
