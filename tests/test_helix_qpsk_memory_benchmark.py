import pytest
from experiments.helix_qpsk_memory_benchmark import benchmark


def test_clean_roundtrip():
    report = benchmark(sizes=(8,), trials=2, noise_levels=(0,), windows=(1,))
    assert report["results"][0]["whole_file_success"] == 1


def test_deterministic_quality():
    a = benchmark(sizes=(8,), trials=2, noise_levels=(0.5,), windows=(1, 3))
    b = benchmark(sizes=(8,), trials=2, noise_levels=(0.5,), windows=(1, 3))
    for x, y in zip(a["results"], b["results"]):
        for metric in ("symbol_accuracy", "coverage", "whole_file_success"):
            assert x[metric] == y[metric]
            assert 0 <= x[metric] <= 1
