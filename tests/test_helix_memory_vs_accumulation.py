from experiments.helix_memory_vs_accumulation import run


def test_reproducible_quality_metrics():
    a = run(sizes=(8, 16), trials=2, noise_levels=(0.5,), windows=(1, 3))
    b = run(sizes=(8, 16), trials=2, noise_levels=(0.5,), windows=(1, 3))
    for x, y in zip(a["results"], b["results"]):
        for key in ("symbol_accuracy", "coverage", "whole_sequence_success"):
            assert x[key] == y[key]
        assert 0 <= x["whole_sequence_success"] <= x["symbol_accuracy"] + 1e-12 or x["whole_sequence_success"] == 1
        assert x["peak_python_memory_bytes_median"] >= 0


def test_clean_observations():
    report = run(sizes=(8,), trials=2, noise_levels=(0,), windows=(1, 3))
    assert all(r["whole_sequence_success"] == 1 for r in report["results"])


def test_invalid_window():
    import pytest
    with pytest.raises(ValueError):
        run(windows=(0,))
