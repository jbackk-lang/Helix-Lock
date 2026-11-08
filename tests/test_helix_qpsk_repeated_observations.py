from experiments.helix_qpsk_repeated_observations import benchmark, _decode
from experiments.helix_chiral_signal import transmit


def test_clean_roundtrip():
    report = benchmark(sizes=(8,), trials=2, noise_levels=(0,), repeats=(1, 3, 7))
    assert all(r["whole_file_success"] == 1 for r in report["results"])


def test_matched_quality_reproducible():
    a = benchmark(sizes=(8,), trials=2, noise_levels=(0.9,), repeats=(1, 3))
    b = benchmark(sizes=(8,), trials=2, noise_levels=(0.9,), repeats=(1, 3))
    for x, y in zip(a["results"], b["results"]):
        for k in ("symbol_accuracy", "coverage", "whole_file_success"):
            assert x[k] == y[k]


def test_single_observation_decodes_symbol():
    for symbol in range(4):
        assert _decode([transmit(symbol, 1, sensors=12, noise=0, seed=symbol)]) == symbol
