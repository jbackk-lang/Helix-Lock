"""Roundtrip and selection tests for the experimental branch search."""
import random

import pytest

from experiments.omega_branch_search import (
    LANES, LAGS, forward, inverse, search, split, unsplit,
)


@pytest.mark.parametrize("size", [0, 1, 2, 3, 7, 16, 255, 256, 1025])
@pytest.mark.parametrize("lanes", LANES)
def test_branch_roundtrip(size, lanes):
    data = random.Random(size).randbytes(size)
    assert unsplit(split(data, lanes), lanes) == data


@pytest.mark.parametrize("size", [0, 1, 3, 256, 1025])
@pytest.mark.parametrize("lanes", LANES)
@pytest.mark.parametrize("lag", LAGS)
@pytest.mark.parametrize("method", ["raw", "xor", "sub"])
def test_predictor_roundtrip(size, lanes, lag, method):
    data = random.Random(size + lag).randbytes(size)
    transformed = forward(data, lanes=lanes, lag=lag, method=method)
    assert inverse(transformed, lanes=lanes, lag=lag, method=method) == data


def test_search_reports_selector_overhead():
    data = bytes(range(256)) * 8
    result = search(data)
    assert result["best"]["estimated_bytes_with_selector"] == result["best"]["zlib_bytes"] + 2
    assert result["net_gain_bytes"] == result["baseline_zlib_bytes"] - result["best"]["estimated_bytes_with_selector"]


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        forward(b"hello", lanes=7)
    with pytest.raises(ValueError):
        inverse(b"hello", method="unknown")
