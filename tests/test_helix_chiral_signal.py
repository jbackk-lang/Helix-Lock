import math
import pytest
from experiments.helix_chiral_signal import transmit, decode, trial, run

@pytest.mark.parametrize("symbol", range(4))
@pytest.mark.parametrize("handedness", (-1, 1))
def test_angular_array_recovers_both_with_zero_noise(symbol, handedness):
    angles, phases = transmit(symbol, handedness, noise=0)
    result = decode(angles, phases)
    assert (result["symbol"], result["handedness"]) == (symbol, handedness)

def test_single_sensor_cannot_identify_handedness():
    angles, phases = transmit(2, 1, sensors=1, noise=0)
    result = decode(angles, phases)
    assert result["score_margin"] == 0

def test_unknown_quarter_turn_phase_offset_corrupts_payload_not_chirality():
    x = trial(42, common_phase=math.pi/2, calibrated_phase=0, noise=0)
    y = trial(42, common_phase=math.pi/2, calibrated_phase=math.pi/2, noise=0)
    assert x["handedness_correct"] and not x["symbol_correct"]
    assert y["both_correct"]

def test_mirror_equivariance_under_angle_reflection():
    angles, phases = transmit(3, 1, noise=0)
    reflected = decode([-a for a in angles], phases)
    assert reflected["handedness"] == -1
    assert reflected["symbol"] == 3

def test_reproducible_results():
    assert run([12, 13]) == run([12, 13])
    assert len(run([12, 13])["results"]) == 45

def test_validation():
    with pytest.raises(ValueError):
        transmit(0, 1, sensors=0)
    with pytest.raises(ValueError):
        transmit(0, 0)
    with pytest.raises(ValueError):
        decode([], [])
