"""Experimental, read-only TIMDR projection for AIRP ledger metadata.

This module does not participate in cryptography or authorization. It consumes
already-recorded, secret-free AIRP events and emits descriptive M/S features.
It is a telemetry adapter, not an intrusion detector.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean, pstdev
from typing import Iterable, Mapping, Any

_ALLOWED_TYPES = {
    "counter_observed", "access_granted", "access_denied",
    "representation_verified", "rotation_committed", "rotation_rejected",
    "checkpoint_created", "quorum_pending", "quorum_confirmed",
}


@dataclass(frozen=True)
class TIMDRObservation:
    """One fixed-window summary; no plaintext, keys, or ciphertext included."""
    start_utc: str
    end_utc: str
    event_count: int
    denied_count: int
    rotation_count: int
    rejected_count: int
    mean_interarrival_seconds: float
    interarrival_drift: float
    event_rate_anomaly: bool


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("event timestamps must include a timezone")
    return parsed


def project_airp_events(
    events: Iterable[Mapping[str, Any]], *, window_size: int = 16,
) -> tuple[TIMDRObservation, ...]:
    """Project chronological AIRP metadata into non-overlapping M/S windows.

    Input records need sequence, timestamp_utc, event_type. Payload content,
    object IDs, hashes, and all cryptographic material are deliberately ignored.
    Anomaly flag is descriptive (> mean + 2 population SD across this input);
    it is not an attack verdict or an authorization signal.
    """
    if not isinstance(window_size, int) or isinstance(window_size, bool) or window_size < 3:
        raise ValueError("window_size must be an integer >= 3")
    rows = []
    previous_sequence = 0
    for event in events:
        sequence = event.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= previous_sequence:
            raise ValueError("events must have strictly increasing integer sequence numbers")
        previous_sequence = sequence
        kind = event.get("event_type")
        if not isinstance(kind, str):
            raise ValueError("event_type must be a string")
        if kind not in _ALLOWED_TYPES:
            # Unknown event types are not silently assigned security semantics.
            continue
        rows.append((_timestamp(str(event["timestamp_utc"])), kind))
    rows.sort(key=lambda item: item[0])
    if not rows:
        return ()

    intervals = [(rows[i][0] - rows[i-1][0]).total_seconds()
                 for i in range(1, len(rows))]
    rates = []
    for offset in range(0, len(rows), window_size):
        chunk = rows[offset:offset + window_size]
        if len(chunk) < 2:
            continue
        times = [item[0] for item in chunk]
        gaps = [(times[i] - times[i-1]).total_seconds() for i in range(1, len(times))]
        avg_gap = mean(gaps)
        drift = 0.0 if len(gaps) < 2 else gaps[-1] - gaps[0]
        rates.append((offset, chunk, avg_gap, drift, len(chunk) / max((times[-1]-times[0]).total_seconds(), 1e-9)))
    baseline = [entry[4] for entry in rates]
    center = mean(baseline) if baseline else 0.0
    spread = pstdev(baseline) if len(baseline) > 1 else 0.0
    output = []
    for _, chunk, avg_gap, drift, rate in rates:
        kinds = [kind for _, kind in chunk]
        output.append(TIMDRObservation(
            start_utc=chunk[0][0].isoformat(),
            end_utc=chunk[-1][0].isoformat(),
            event_count=len(chunk),
            denied_count=sum(k in {"access_denied", "rotation_rejected"} for k in kinds),
            rotation_count=sum(k == "rotation_committed" for k in kinds),
            rejected_count=sum(k == "rotation_rejected" for k in kinds),
            mean_interarrival_seconds=avg_gap,
            interarrival_drift=drift,
            event_rate_anomaly=bool(spread > 0 and rate > center + 2 * spread),
        ))
    return tuple(output)



def project_ledger(
    ledger: Any, *, object_id: str | None = None, window_size: int = 16,
) -> tuple[TIMDRObservation, ...]:
    """Read AIRPIntegrityLedger.events() and project its metadata.

    The adapter is intentionally pull-only: it does not subscribe to or alter
    ledger writes, and it cannot affect encryption, key rotation, or access
    decisions. The ledger remains the source of truth.
    """
    events_method = getattr(ledger, "events", None)
    if not callable(events_method):
        raise TypeError("ledger must expose events(object_id=None)")
    events = events_method(object_id)
    return project_airp_events(events, window_size=window_size)
