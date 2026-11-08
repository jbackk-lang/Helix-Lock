"""Simple majority consensus for repeated QPSK sensor observations.

Independent votes here mean separate simulated channel observations; sensors
within one observation share a corruption source and do not count as votes.
Abstain on ties or insufficient supermajority. This is not authentication.
"""
from __future__ import annotations

import math
from collections import Counter

from experiments.helix_chiral_signal import PHASES, wrap
from experiments.helix_resonance_filter import decode as decode_joint


def _vote(observation):
    angles, phases = observation
    if not angles or len(angles) != len(phases):
        raise ValueError("invalid observation")
    residuals = [phase - angle for angle, phase in zip(angles, phases)]
    phase = math.atan2(sum(math.sin(x) for x in residuals),
                       sum(math.cos(x) for x in residuals))
    error, symbol = min((abs(wrap(phase - target)), i)
                        for i, target in enumerate(PHASES))
    return symbol if error <= math.pi / 8 else None


def decode_consensus(observations, *, quorum=2 / 3):
    if not 0.5 < quorum <= 1:
        raise ValueError("quorum must be in (0.5, 1]")
    if not observations:
        raise ValueError("at least one observation required")
    votes = [_vote(obs) for obs in observations]
    counts = Counter(v for v in votes if v is not None)
    if not counts:
        return None
    winner, count = counts.most_common(1)[0]
    # Quorum denominator is ALL observations, including abstentions.
    # Avoid rounding/float boundary ambiguity.
    if count / len(votes) < quorum:
        return None
    return winner


def benchmark(*, sizes=(16, 64), trials=6, noise_levels=(0.5, 0.9),
              repeats=(3, 7), corruption_rates=(0, 0.15), seed=20261108):
    import random
    from experiments.helix_chiral_signal import transmit
    from experiments.helix_phase_coherence import decode_adaptive
    rows = []
    for noise in noise_levels:
        for size in sizes:
            for copies in repeats:
                for corruption in corruption_rates:
                    counts = {m: 0 for m in ("circular", "resonance", "adaptive", "consensus")}
                    accepted = 0
                    total = 0
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
                            predictions = {
                                "circular": decode_joint(observations, "circular"),
                                "resonance": decode_joint(observations, "resonance"),
                                "adaptive": decode_adaptive(observations)[0],
                                "consensus": decode_consensus(observations),
                            }
                            for method, prediction in predictions.items():
                                counts[method] += prediction == symbol
                            accepted += predictions["consensus"] is not None
                            total += 1
                    rows.append({
                        "noise": noise, "input_bytes": size, "repeats": copies,
                        "corruption_rate": corruption, "symbols": total,
                        "accuracy": {m: counts[m] / total for m in counts},
                        "consensus_coverage": accepted / total,
                    })
    return {"format": "helix-consensus-v1", "seed": seed,
            "note": "Synthetic matched observations. Consensus abstentions count "
                    "as incorrect in accuracy; coverage reported separately. "
                    "Not a cryptographic consensus protocol.",
            "results": rows}


if __name__ == "__main__":
    import json
    print(json.dumps(benchmark(), indent=2))
