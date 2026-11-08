import math
import pytest

from experiments.helix_chiral_signal import transmit
from experiments.helix_symbol_consensus import decode_consensus, benchmark


def observation(symbol):
    return transmit(symbol, 1, sensors=12, noise=0, seed=symbol)


def test_unanimous_clean_symbols():
    for symbol in range(4):
        assert decode_consensus([observation(symbol)] * 3) == symbol


def test_two_of_three_majority():
    assert decode_consensus([observation(2), observation(2), observation(1)]) == 2


def test_tie_abstains():
    assert decode_consensus([observation(0), observation(1)]) is None


def test_abstentions_count_against_quorum():
    angles, phases = observation(0)
    abstain = (angles, [p + math.pi / 4 for p in phases])
    assert decode_consensus([observation(0), abstain, abstain]) is None


def test_invalid_input():
    with pytest.raises(ValueError):
        decode_consensus([])
    with pytest.raises(ValueError):
        decode_consensus([observation(0)], quorum=0.5)


def test_matched_report():
    result = benchmark(sizes=(8,), trials=2, noise_levels=(0.5,),
                       repeats=(3,), corruption_rates=(0, 0.15))
    assert len(result["results"]) == 2
    for row in result["results"]:
        assert set(row["accuracy"]) == {"circular", "resonance", "adaptive", "consensus"}
        assert 0 <= row["consensus_coverage"] <= 1
