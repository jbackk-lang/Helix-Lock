"""CounterLock integration with the durable AIRP integrity ledger."""
from __future__ import annotations

import hashlib

from .airp_ledger import AIRPIntegrityLedger
from .cipher import HelixProError
from .counter_lock import CounterLock


class AIRPCounterLock:
    """Reject CounterLock replays using an independently anchored AIRP ledger.

    A counter is consumed when it is recorded. If the process crashes after
    recording but before the caller persists next_blob, recovery is fail-closed:
    restore the newest valid file or perform an explicit administrative repair.
    """

    def __init__(self, key: bytes, ledger: AIRPIntegrityLedger, object_id: str):
        if not object_id:
            raise HelixProError("object_id must be non-empty")
        self._lock = CounterLock(key)
        self._ledger = ledger
        self._object_id = object_id

    def unlock_and_advance(self, blob: bytes) -> tuple[bytes, int, bytes]:
        plaintext, counter = self._lock.unlock(blob)
        self._ledger.observe_counter(
            self._object_id, counter, hashlib.sha256(blob).hexdigest()
        )
        next_blob = self._lock.lock(plaintext, counter + 1)
        return plaintext, counter, next_blob
