import pytest

from experiments.helix_native_history_comparison import compare


def test_deterministic_matched_comparison():
    a = compare(seeds=range(3), samples=12, window=3)
    b = compare(seeds=range(3), samples=12, window=3)
    assert a == b
    assert a["metrics"]["instant"]["coverage"] <= 1
    assert a["metrics"]["history"]["coverage"] <= 1
    assert len(a["metrics"]["history"]["reversal_delays"]) == 3


def test_window_one_matches_instantaneous_when_decided():
    report = compare(seeds=range(4), samples=12, window=1, noise=0)
    assert report["metrics"]["instant"]["accuracy_with_abstentions"] == report["metrics"]["history"]["accuracy_with_abstentions"]


def test_invalid_parameters():
    with pytest.raises(ValueError):
        compare(window=0)
