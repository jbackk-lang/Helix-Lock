"""AIRP monitor: version/integrity state and access-event auditing.

This is a small policy helper, not an intrusion detector or durable trusted
counter. Persist its state in a protected external store for rollback detection
across process restarts. Never log plaintext, keys, passwords, or tokens.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from .cipher import HelixProError


@dataclass(frozen=True)
class RepresentationState:
    version: int
    key_id: str
    blob_sha256: str


@dataclass(frozen=True)
class AccessEvent:
    timestamp_utc: str
    outcome: str
    version: int
    key_id: str
    blob_sha256: str


class AIRPMonitor:
    """Track one object's expected representation and append access events.

    The caller supplies an independently protected initial state on startup.
    For multi-process or persistent use, store/compare state transactionally
    in a trusted database or remote append-only service.
    """

    def __init__(self, state: RepresentationState):
        self._state = state
        self._events: list[AccessEvent] = []

    @staticmethod
    def fingerprint(blob: bytes) -> str:
        return hashlib.sha256(blob).hexdigest()

    @property
    def state(self) -> RepresentationState:
        return self._state

    @property
    def events(self) -> tuple[AccessEvent, ...]:
        return tuple(self._events)

    def verify_current(self, blob: bytes, *, version: int, key_id: str) -> bool:
        """Return true only for the exact currently registered representation."""
        return (
            version == self._state.version
            and key_id == self._state.key_id
            and self.fingerprint(blob) == self._state.blob_sha256
        )

    def record_access(self, *, outcome: str) -> AccessEvent:
        """Record 'granted' or 'denied'; callers decide outcome after auth."""
        if outcome not in {"granted", "denied"}:
            raise HelixProError("outcome must be 'granted' or 'denied'")
        event = AccessEvent(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            outcome=outcome,
            version=self._state.version,
            key_id=self._state.key_id,
            blob_sha256=self._state.blob_sha256,
        )
        self._events.append(event)
        return event

    def accept_rotation(
        self,
        new_blob: bytes,
        *,
        new_version: int,
        new_key_id: str,
    ) -> RepresentationState:
        """Advance state only to a strictly newer version and new key ID."""
        if new_version != self._state.version + 1:
            raise HelixProError("new_version must be exactly current version + 1")
        if not new_key_id or new_key_id == self._state.key_id:
            raise HelixProError("new_key_id must be non-empty and differ from current key_id")
        self._state = RepresentationState(
            version=new_version,
            key_id=new_key_id,
            blob_sha256=self.fingerprint(new_blob),
        )
        return self._state
