"""Stage desktop file results and atomically replace the selected destination.

The caller must explicitly confirm overwrites in the UI before invoking this.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import Callable


def validate_distinct_paths(source: str, destination: str) -> None:
    """Reject identical paths, including symlink and hard-link aliases."""
    if os.path.abspath(source) == os.path.abspath(destination):
        raise ValueError("Output file must differ from source file.")
    if os.path.exists(destination) and os.path.samefile(source, destination):
        raise ValueError("Output file must differ from source file.")


def atomic_file_result(source: str, destination: str, produce: Callable[[str], None]) -> None:
    """Produce to a sibling temporary file; replace destination only on success."""
    validate_distinct_paths(source, destination)
    target = Path(destination)
    fd, temporary = tempfile.mkstemp(prefix=".helix-pending-", dir=target.parent)
    os.close(fd)
    try:
        produce(temporary)
        # A producer may replace the temporary path, so check its result exists.
        if not os.path.isfile(temporary):
            raise OSError("Operation did not create an output file")
        validate_distinct_paths(source, destination)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
