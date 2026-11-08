import json
import pytest

from experiments.helix_native_benchmark import benchmark, perturb
from experiments.helix_native_codec import encode_bytes, decode_bytes


def test_benchmark_report_structure_and_clean_roundtrip():
    report = benchmark(sizes=(0, 8), trials=2, noise_levels=(0.0,))
    assert report["format"] == "helix-native-benchmark-v0"
    assert len(report["results"]) == 2
    assert all(row["noise_roundtrip_rate"]["0.0"] == 1.0 for row in report["results"])
    assert report["results"][0]["expansion_ratio_median"] is None
    assert report["results"][1]["expansion_ratio_median"] > 1


def test_perturb_is_reproducible():
    encoded = encode_bytes(b"abc")
    assert perturb(encoded, sigma=0.1, seed=11) == perturb(encoded, sigma=0.1, seed=11)


def test_noise_zero_is_reversible():
    encoded = encode_bytes(b"hello")
    assert decode_bytes(perturb(encoded, sigma=0, seed=4)) == b"hello"


def test_large_noise_is_detected_or_rejected():
    encoded = encode_bytes(b"hello")
    changed = perturb(encoded, sigma=3.0, seed=4)
    with pytest.raises(ValueError):
        decode_bytes(changed)


def test_bad_noise_rejected():
    with pytest.raises(ValueError):
        perturb(encode_bytes(b"a"), sigma=-0.1, seed=0)
