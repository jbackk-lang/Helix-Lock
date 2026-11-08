"""Recovery classification for a guarded replay receiver after a crash.

Never silently repair a checkpoint mismatch. An external trust authority may
hold a checkpoint newer than local SQLite due to an interrupted commit.
This module classifies the state; operator-supervised restoration is required.
"""
from __future__ import annotations

import hmac
from pathlib import Path
from typing import Callable

from experiments.helix_replay_state_checkpoint import seal_state


class RecoveryRequired(RuntimeError):
    pass


def inspect_replay_state(database: str | Path, integrity_key: bytes,
                         trusted_checkpoint: bytes) -> str:
    """Return 'consistent' or raise RecoveryRequired (fail closed)."""
    if len(trusted_checkpoint) != 32:
        raise RecoveryRequired("invalid or missing trusted checkpoint")
    try:
        current = seal_state(database, integrity_key)
    except Exception as exc:
        raise RecoveryRequired("cannot verify local replay state") from exc
    if not hmac.compare_digest(current, trusted_checkpoint):
        raise RecoveryRequired(
            "local state and trusted checkpoint diverged; block admission and "
            "require independently verified recovery"
        )
    return "consistent"


def verify_before_resume(database: str | Path, integrity_key: bytes,
                         read_trusted_checkpoint: Callable[[], bytes]) -> None:
    try:
        checkpoint = read_trusted_checkpoint()
    except Exception as exc:
        raise RecoveryRequired("trusted checkpoint unavailable") from exc
    inspect_replay_state(database, integrity_key, checkpoint)
