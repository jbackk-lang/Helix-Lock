"""Bounded deterministic historical feature memory for AIRP metadata.

This is a rebuildable analytical index, never the audit source of truth.
It consumes only sequence, timestamp and event type/outcome metadata, emits
fixed-size summaries, and never retains raw event payloads or identifiers.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from statistics import mean, pstdev
from typing import Any, Iterable, Mapping

from .cipher import HelixProError

ALGORITHM_VERSION = "airp-history-window-v1"
_ALLOWED_TYPES = {
    "registered", "rotated", "access", "counter_observed",
    "access_granted", "access_denied", "representation_verified",
    "rotation_committed", "rotation_rejected", "checkpoint_created",
    "quorum_pending", "quorum_confirmed",
}


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise HelixProError("event timestamp must include a timezone")
    return parsed


@dataclass(frozen=True)
class HistoryWindow:
    algorithm_version: str
    first_sequence: int
    last_sequence: int
    start_utc: str
    end_utc: str
    event_count: int
    event_type_counts: dict[str, int]
    denied_count: int
    rotation_count: int
    mean_interarrival_seconds: float
    interarrival_pstdev_seconds: float
    interarrival_drift_seconds: float
    source_checkpoint_sha256: str
    summary_sha256: str


class AIRPHistoryMemory:
    """Incremental fixed-window feature memory with bounded working state.

    source_checkpoint_sha256 must identify a separately verified ledger
    checkpoint covering the input prefix. This class does not verify or create
    that checkpoint; callers must do so with AIRPIntegrityLedger/TrustAnchor.
    """

    def __init__(self, *, window_size: int = 64, first_sequence: int = 1):
        if not isinstance(window_size, int) or isinstance(window_size, bool) or window_size < 3:
            raise HelixProError("window_size must be an integer >= 3")
        if not isinstance(first_sequence, int) or isinstance(first_sequence, bool) or first_sequence < 1:
            raise HelixProError("first_sequence must be a positive integer")
        self.window_size = window_size
        self._expected_sequence = first_sequence
        self._buffer: list[tuple[int, datetime, str, str | None]] = []
        self._summaries: list[HistoryWindow] = []

    @property
    def pending_events(self) -> int:
        return len(self._buffer)

    @property
    def summaries(self) -> tuple[HistoryWindow, ...]:
        return tuple(self._summaries)

    @property
    def retained_event_count(self) -> int:
        return len(self._buffer)

    def consume(self, events: Iterable[Mapping[str, Any]], *, source_checkpoint_sha256: str) -> tuple[HistoryWindow, ...]:
        if not isinstance(source_checkpoint_sha256, str) or len(source_checkpoint_sha256) != 64:
            raise HelixProError("source checkpoint must be a SHA-256 hex digest")
        try:
            int(source_checkpoint_sha256, 16)
        except ValueError as exc:
            raise HelixProError("source checkpoint must be a SHA-256 hex digest") from exc

        emitted = []
        for event in events:
            sequence = event.get("sequence")
            if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence != self._expected_sequence:
                raise HelixProError(f"history sequence gap or replay: expected {self._expected_sequence}")
            kind = event.get("event_type")
            if not isinstance(kind, str) or kind not in _ALLOWED_TYPES:
                raise HelixProError("unsupported history event_type")
            timestamp = _parse_time(str(event.get("timestamp_utc", "")))
            payload = event.get("payload")
            outcome = payload.get("outcome") if isinstance(payload, Mapping) else None
            if kind == "access" and outcome not in {"granted", "denied"}:
                raise HelixProError("access event requires a known outcome")
            self._buffer.append((sequence, timestamp, kind, outcome))
            self._expected_sequence += 1
            if len(self._buffer) == self.window_size:
                summary = self._summarize(source_checkpoint_sha256)
                self._summaries.append(summary)
                emitted.append(summary)
                self._buffer.clear()
        return tuple(emitted)

    def _summarize(self, checkpoint_hash: str) -> HistoryWindow:
        rows = self._buffer
        times = [row[1] for row in rows]
        gaps = [(times[i] - times[i - 1]).total_seconds() for i in range(1, len(times))]
        kinds = Counter(row[2] for row in rows)
        denied = sum((kind == "access" and outcome == "denied") or kind in {"access_denied", "rotation_rejected"} for _, _, kind, outcome in rows)
        rotations = sum(kind in {"rotated", "rotation_committed"} for _, _, kind, _ in rows)
        material = {
            "algorithm_version": ALGORITHM_VERSION,
            "first_sequence": rows[0][0],
            "last_sequence": rows[-1][0],
            "start_utc": times[0].isoformat(),
            "end_utc": times[-1].isoformat(),
            "event_count": len(rows),
            "event_type_counts": dict(sorted(kinds.items())),
            "denied_count": denied,
            "rotation_count": rotations,
            "mean_interarrival_seconds": mean(gaps) if gaps else 0.0,
            "interarrival_pstdev_seconds": pstdev(gaps) if len(gaps) > 1 else 0.0,
            "interarrival_drift_seconds": (gaps[-1] - gaps[0]) if len(gaps) > 1 else 0.0,
            "source_checkpoint_sha256": checkpoint_hash.lower(),
        }
        digest = hashlib.sha256(_canonical(material)).hexdigest()
        return HistoryWindow(**material, summary_sha256=digest)

    def export(self) -> tuple[dict, ...]:
        """Return deterministic summaries; incomplete trailing events are omitted."""
        return tuple(asdict(item) for item in self._summaries)