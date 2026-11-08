"""Experimental, uncertainty-aware Helix signal intelligence.

No production AIRP/security integration. The chirality evidence marginalizes
the common phase by fitting each winding independently. Payload requires a
phase reference. Confidence is a heuristic score, not a calibrated probability.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math

from experiments.helix_chiral_signal import PHASES, wrap


@dataclass(frozen=True)
class Observation:
    timestamp: float
    angles: tuple[float, ...]
    phases: tuple[float, ...]
    calibrated_phase: float | None = None

    def __post_init__(self):
        if not math.isfinite(self.timestamp):
            raise ValueError("timestamp must be finite")
        if not self.angles or len(self.angles) != len(self.phases):
            raise ValueError("angular samples must be aligned and nonempty")
        if any(not math.isfinite(x) for x in self.angles + self.phases):
            raise ValueError("angular samples must be finite")
        if self.calibrated_phase is not None and not math.isfinite(self.calibrated_phase):
            raise ValueError("calibration must be finite")


@dataclass(frozen=True)
class Assessment:
    timestamp: float
    handedness: int | None
    symbol: int | None
    status: str
    evidence: float
    phase_coherence: float
    anomaly: bool
    history_length: int


class HelixChiralIntelligence:
    """Isolated experimental observer; never authorizes a security action."""

    def __init__(self, *, memory_size=16, evidence_threshold=0.20,
                 coherence_threshold=0.65):
        if memory_size < 1 or not 0 <= evidence_threshold <= 1 or not 0 <= coherence_threshold <= 1:
            raise ValueError("invalid thresholds or memory size")
        self._history = deque(maxlen=memory_size)
        self.evidence_threshold = evidence_threshold
        self.coherence_threshold = coherence_threshold

    @property
    def history(self):
        return tuple(self._history)

    def observe(self, observation: Observation) -> Assessment:
        if self._history and observation.timestamp <= self._history[-1].timestamp:
            raise ValueError("timestamps must increase")

        candidates = []
        n = len(observation.angles)
        for h in (-1, 1):
            # Fit nuisance common phase separately for each winding hypothesis.
            re = sum(math.cos(p - h * a) for a, p in zip(observation.angles, observation.phases))
            im = sum(math.sin(p - h * a) for a, p in zip(observation.angles, observation.phases))
            coherence = math.hypot(re, im) / n
            candidates.append((coherence, h, math.atan2(im, re)))
        candidates.sort(reverse=True)
        best, second = candidates
        evidence = max(0.0, best[0] - second[0])
        enough = (n >= 2 and evidence >= self.evidence_threshold
                  and best[0] >= self.coherence_threshold)
        handedness = best[1] if enough else None

        symbol = None
        if handedness is not None and observation.calibrated_phase is not None:
            relative = wrap(best[2] - observation.calibrated_phase)
            errors = sorted((abs(wrap(relative - phase)), j)
                            for j, phase in enumerate(PHASES))
            # Abstain when phase is too far from a known QPSK symbol.
            if errors[0][0] <= math.pi / 8:
                symbol = errors[0][1]

        previous = next((x for x in reversed(self._history)
                         if x.handedness is not None), None)
        reversal = (handedness is not None and previous is not None
                    and previous.handedness != handedness)
        anomaly = reversal or (best[0] < self.coherence_threshold)
        status = ("ambiguous" if handedness is None else
                  "chirality_only" if symbol is None else "decoded")
        result = Assessment(observation.timestamp, handedness, symbol, status,
                            round(evidence, 6), round(best[0], 6),
                            anomaly, len(self._history) + 1)
        self._history.append(result)
        return result
