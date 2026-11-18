"""Desktop output staging and source protection."""
from pathlib import Path

import pytest

from helix_pro.safe_output import atomic_file_result, validate_distinct_paths


def test_success_replaces_destination(tmp_path):
    src = tmp_path / "input"
    dst = tmp_path / "output"
    src.write_bytes(b"source")
    dst.write_bytes(b"previous")
    atomic_file_result(str(src), str(dst), lambda temp: Path(temp).write_bytes(b"result"))
    assert src.read_bytes() == b"source"
    assert dst.read_bytes() == b"result"
    assert not list(tmp_path.glob(".helix-pending-*"))


def test_failure_preserves_existing_destination(tmp_path):
    src = tmp_path / "input"
    dst = tmp_path / "output"
    src.write_bytes(b"source")
    dst.write_bytes(b"previous")

    def fail(temp):
        Path(temp).write_bytes(b"partial")
        raise ValueError("simulated failure")

    with pytest.raises(ValueError, match="simulated"):
        atomic_file_result(str(src), str(dst), fail)
    assert dst.read_bytes() == b"previous"
    assert not list(tmp_path.glob(".helix-pending-*"))


def test_same_file_rejected(tmp_path):
    src = tmp_path / "input"
    src.write_bytes(b"source")
    with pytest.raises(ValueError):
        validate_distinct_paths(str(src), str(src))


def test_hard_link_alias_rejected(tmp_path):
    src = tmp_path / "input"
    alias = tmp_path / "alias"
    src.write_bytes(b"source")
    try:
        alias.hardlink_to(src)
    except OSError:
        pytest.skip("hard links not supported")
    with pytest.raises(ValueError):
        atomic_file_result(str(src), str(alias), lambda temp: Path(temp).write_bytes(b"oops"))
    assert src.read_bytes() == b"source"
