"""Independent branch predictor reversibility and selector scoring."""
import random

import pytest

from experiments.omega_branch_independent import (
    CHOICES, decode_independent, encode_independent, search,
)
from experiments.omega_branch_search import LANES


@pytest.mark.parametrize("size", [0, 1, 2, 3, 7, 16, 256, 1025])
@pytest.mark.parametrize("lanes", LANES)
def test_independent_branch_roundtrip(size, lanes):
    data = random.Random(size * 3 + lanes).randbytes(size)
    selectors = [CHOICES[(i * 7 + size) % len(CHOICES)] for i in range(lanes)]
    assert decode_independent(encode_independent(data, lanes, selectors),
                              lanes, selectors) == data


def test_independent_predictors_can_differ():
    data = bytes(range(256)) * 3
    selectors = [("raw", 1), ("sub", 1), ("xor", 3)]
    encoded = encode_independent(data, 3, selectors)
    assert decode_independent(encoded, 3, selectors) == data


def test_search_selector_overhead_and_recovery():
    result = search(bytes(range(256)) * 2)
    best = result["best"]
    assert best["estimated_bytes_with_selectors"] == best["zlib_bytes"] + 1 + best["lanes"]


def test_wrong_selector_count_rejected():
    with pytest.raises(ValueError):
        encode_independent(b"abc", 3, [("raw", 1)])
    with pytest.raises(ValueError):
        decode_independent(b"abc", 3, [("raw", 1)])
