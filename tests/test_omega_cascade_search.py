"""Regression checks for two-stage experimental Omega transforms."""
import random

import pytest

from experiments.omega_cascade_search import (
    STAGES, compress_branches, restore, search, transform,
)
from experiments.omega_branch_search import LANES


@pytest.mark.parametrize("size", [0, 1, 2, 3, 16, 255, 256, 1025])
@pytest.mark.parametrize("lanes", LANES)
@pytest.mark.parametrize("stage", STAGES)
def test_one_stage_roundtrip(size, lanes, stage):
    data = random.Random(size + lanes).randbytes(size)
    assert restore(transform(data, lanes, (stage,)), lanes, (stage,)) == data


@pytest.mark.parametrize("lanes", LANES)
@pytest.mark.parametrize("stages", [
    (("sub", 1), ("xor", 3)),
    (("xor", 256), ("sub", 1)),
    (("sub", 3), ("sub", 256)),
    (("raw", 1), ("xor", 1)),
])
def test_two_stage_roundtrip(lanes, stages):
    data = random.Random(lanes).randbytes(1031)
    assert restore(transform(data, lanes, stages), lanes, stages) == data


def test_separate_streams_have_overhead():
    assert compress_branches(b"", 1) > 0
    assert compress_branches(b"", 8) > compress_branches(b"", 1)


def test_raw_baseline_is_not_worsened():
    result = search(bytes(range(256)) * 4)
    assert result["best"]["bytes"] <= result["baseline_bytes"]
    assert result["candidates"] > 0


def test_invalid_stages():
    with pytest.raises(ValueError):
        transform(b"abc", 1, ())
    with pytest.raises(ValueError):
        restore(b"abc", 7, (("raw", 1),))
