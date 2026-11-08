import math
import pytest
from experiments.helix_chiral_signal import decode
from experiments.helix_chiral_signal_channel import channel, trial, run


@pytest.mark.parametrize("symbol", range(4))
@pytest.mark.parametrize("handedness", (-1, 1))
def test_noiseless_direct_channel(symbol, handedness):
    angles, phases = channel(symbol, handedness, noise=0)
    result = decode(angles, phases)
    assert (result["symbol"], result["handedness"]) == (symbol, handedness)


def test_doppler_phase_offset_requires_payload_calibration():
    a = trial(42, noise=0, doppler_phase=math.pi/2)
    b = trial(42, noise=0, doppler_phase=math.pi/2, calibrated_phase=math.pi/2)
    assert a == (False, True)
    assert b == (True, True)


def test_opposite_winding_strong_echo_can_flip_decoded_handedness():
    angles, phases = channel(0, 1, noise=0, reflection_gain=2)
    result = decode(angles, phases)
    assert result["handedness"] == -1


def test_reproducible_channel():
    assert run([42, 43]) == run([42, 43])
    assert len(run([42, 43])["results"]) == 12  # zero-drift calibration cases coincide


def test_invalid_echo():
    with pytest.raises(ValueError):
        channel(0, 1, reflection_gain=-1)
