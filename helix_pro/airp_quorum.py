"""Quorum wrapper for multiple independently operated AIRP trust anchors.

The default safety assumption is a strict majority of configured witnesses.
Witnesses must be administered in separate trust domains; replicas under one
administrator do not provide meaningful administrative independence.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Iterable

from .airp_ledger import TrustAnchor
from .cipher import HelixProError


class QuorumTrustAnchor(TrustAnchor):
    """Require a quorum for checkpoint publication and latest-state reads."""

    def __init__(self, anchors: Iterable[TrustAnchor], *, quorum: int | None = None):
        self._anchors = tuple(anchors)
        if not self._anchors:
            raise HelixProError("at least one TrustAnchor is required")
        if quorum is None:
            quorum = len(self._anchors) // 2 + 1
        if type(quorum) is not int or quorum < 1 or quorum > len(self._anchors):
            raise HelixProError("quorum must be an integer between 1 and anchor count")
        if quorum <= len(self._anchors) // 2:
            raise HelixProError("quorum must be a strict majority")
        self.quorum = quorum

    def publish_checkpoint(self, checkpoint: bytes) -> None:
        successes = 0
        for anchor in self._anchors:
            try:
                anchor.publish_checkpoint(checkpoint)
                successes += 1
            except Exception:
                continue
        if successes < self.quorum:
            raise HelixProError(
                f"AIRP checkpoint reached {successes}/{len(self._anchors)} anchors; "
                f"{self.quorum} required"
            )

    def latest_checkpoint(self) -> bytes | None:
        observed: list[bytes] = []
        errors = 0
        for anchor in self._anchors:
            try:
                value = anchor.latest_checkpoint()
                if value is not None:
                    observed.append(value)
            except Exception:
                errors += 1
        if not observed and errors == 0:
            return None
        groups: dict[tuple[int, str], list[bytes]] = {}
        for raw in observed:
            try:
                parsed = json.loads(raw.decode("utf-8"))
                sequence, head_hash = parsed["sequence"], parsed["head_hash"]
                if type(sequence) is not int or sequence < 0 or not isinstance(head_hash, str):
                    continue
                groups.setdefault((sequence, head_hash), []).append(raw)
            except Exception:
                continue
        winners = [(key, values) for key, values in groups.items() if len(values) >= self.quorum]
        if not winners:
            raise HelixProError(
                f"AIRP anchors did not return a matching checkpoint quorum "
                f"({len(observed)} responses, {errors} errors, {self.quorum} required)"
            )
        winners.sort(key=lambda item: item[0][0], reverse=True)
        return winners[0][1][0]
