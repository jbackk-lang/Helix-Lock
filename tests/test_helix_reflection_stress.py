import math
import pytest

from experiments.helix_reflection_stress import reflected_observation, benchmark
from experiments.helix_symbol_consensus import decode_consensus


def test_clean_reflection_free_symbols():
    for symbol in range(4):
        obs = [reflected_observation(symbol, noise=0, seed=i) for i in range(3)]
        assert decode_consensus(obs) == symbol


def test_zero_echo_amplitude_independent_of_echo_phase():
    a = reflected_observation(2, echo_amplitude=0, echo_phase=0, noise=0, seed=1)
    b = reflected_observation(2, echo_amplitude=0, echo_phase=math.pi, noise=0, seed=1)
    assert a == b


def test_echo_scenario_report():
    report = benchmark(trials=2, symbols_per_trial=16, copies=(3,),
                       noise_levels=(0.25,), echo_amplitudes=(0, 0.85),
                       echo_phases=(math.pi / 2,))
    assert len(report["results"]) == 2
    for row in report["results"]:
        assert set(row["accuracy"]) == {"circular", "resonance", "adaptive", "consensus"}
        assert 0 <= row["consensus_coverage"] <= 1


def test_invalid_echo_amplitude():
    with pytest.raises(ValueError):
        reflected_observation(0, echo_amplitude=1.0)
