import pytest

from experiments.helix_phase_coherence import coherence, decode_adaptive, benchmark
from experiments.helix_chiral_signal import transmit


def test_clean_coherent_signal_uses_baseline():
    for symbol in range(4):
        observations = [transmit(symbol, 1, sensors=12, noise=0, seed=i)
                        for i in range(3)]
        guess, method, score = decode_adaptive(observations)
        assert guess == symbol
        assert method == "circular"
        assert score == pytest.approx(1.0)


def test_disagreement_selects_robust():
    obs = [transmit(0, 1, sensors=12, noise=0, seed=i) for i in range(3)]
    angles, phases = obs[-1]
    obs[-1] = (angles, [p + 3.141592653589793 for p in phases])
    _, method, score = decode_adaptive(obs)
    assert score < 0.85
    assert method == "resonance"


def test_matched_benchmark_reports_all_estimators():
    result = benchmark(sizes=(8,), trials=2, noise_levels=(0.5,),
                       repeats=(3,), corruption_rates=(0, 0.15))
    assert len(result["results"]) == 2
    for row in result["results"]:
        assert set(row["symbol_accuracy"]) == {"circular", "resonance", "adaptive"}
        assert all(0 <= value <= 1 for value in row["symbol_accuracy"].values())


def test_bad_input_rejected():
    with pytest.raises(ValueError):
        coherence([])
    with pytest.raises(ValueError):
        decode_adaptive([([0], [0])], coherence_threshold=2)
