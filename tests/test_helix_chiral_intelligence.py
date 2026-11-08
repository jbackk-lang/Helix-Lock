import math
import pytest

from experiments.helix_chiral_signal import transmit
from experiments.helix_chiral_signal_channel import channel
from experiments.helix_chiral_intelligence import (
    Assessment, HelixChiralIntelligence, Observation,
)


@pytest.mark.parametrize("symbol", range(4))
@pytest.mark.parametrize("handedness", (-1, 1))
def test_calibrated_direct_signal(symbol, handedness):
    a, p = transmit(symbol, handedness, noise=0)
    result = HelixChiralIntelligence().observe(
        Observation(1, tuple(a), tuple(p), 0))
    assert result.handedness == handedness
    assert result.symbol == symbol
    assert result.status == "decoded"


def test_single_sensor_abstains():
    a, p = transmit(0, 1, sensors=1, noise=0)
    result = HelixChiralIntelligence().observe(
        Observation(1, tuple(a), tuple(p), 0))
    assert result.status == "ambiguous"
    assert result.handedness is None and result.symbol is None


def test_unknown_pilot_preserves_chirality_but_not_payload():
    a, p = transmit(2, -1, noise=0, common_phase=math.pi/2)
    result = HelixChiralIntelligence().observe(Observation(1, tuple(a), tuple(p)))
    assert result.handedness == -1
    assert result.symbol is None
    assert result.status == "chirality_only"


def test_known_pilot_recovers_drifted_payload():
    a, p = transmit(2, -1, noise=0, common_phase=math.pi/2)
    result = HelixChiralIntelligence().observe(
        Observation(1, tuple(a), tuple(p), math.pi/2))
    assert result.symbol == 2


def test_history_flags_reversal_and_is_bounded():
    agent = HelixChiralIntelligence(memory_size=2)
    for t, h in ((1, 1), (2, 1), (3, -1)):
        a, p = transmit(0, h, noise=0)
        result = agent.observe(Observation(t, tuple(a), tuple(p), 0))
    assert result.anomaly
    assert len(agent.history) == 2
    assert agent.history[-1] == result


def test_strong_mirror_echo_does_not_claim_emitter_identity():
    a, p = channel(0, 1, noise=0, reflection_gain=2)
    result = HelixChiralIntelligence().observe(
        Observation(1, tuple(a), tuple(p), 0))
    assert result.handedness == -1  # observed field, not source identity


def test_nonmonotonic_time_rejected():
    agent = HelixChiralIntelligence()
    a, p = transmit(0, 1, noise=0)
    observation = Observation(1, tuple(a), tuple(p))
    agent.observe(observation)
    with pytest.raises(ValueError):
        agent.observe(observation)


def test_bad_observations_rejected():
    with pytest.raises(ValueError):
        Observation(1, (0.0,), ())
    with pytest.raises(ValueError):
        Observation(1, (float("nan"),), (0.0,))
    with pytest.raises(ValueError):
        HelixChiralIntelligence(memory_size=0)
