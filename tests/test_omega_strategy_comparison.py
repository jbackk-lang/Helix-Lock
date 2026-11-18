"""Smoke checks for the Omega head-to-head benchmark."""
import pytest

from benchmarks.omega_strategy_comparison import samples, compare


def test_samples_deterministic():
    assert samples(64, 42) == samples(64, 42)
    assert samples(64, 42)["random"] != samples(64, 43)["random"]
    assert all(len(value) == 64 for value in samples(64, 42).values())


def test_reject_negative_size():
    with pytest.raises(ValueError):
        samples(-1, 42)


@pytest.mark.parametrize("sample", ["random", "gradient", "rows", "rgb", "periodic", "mixed_channels"])
def test_comparison_has_consistent_scores(sample):
    data = samples(64, 7)[sample]
    result = compare(data)
    assert result["input_bytes"] == len(data)
    assert result["winner"]["estimated_bytes"] <= result["baseline_zlib_bytes"]
    assert set(result["strategies"]) == {"common", "independent", "cascade"}
    for item in result["strategies"].values():
        assert item["estimated_bytes"] >= 0
        assert item["search_ms"] >= 0
