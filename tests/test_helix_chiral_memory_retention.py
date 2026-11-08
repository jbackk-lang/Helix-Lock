import pytest
from experiments.helix_chiral_memory_retention import run, run_trial

def test_mirror_pair_has_equal_memory_quality_with_orientation_aware_readout():
    r = run_trial(42, handedness=1, mode="full_cycle_history", orientation_aware=True, disturbance=0.5)
    l = run_trial(42, handedness=-1, mode="full_cycle_history", orientation_aware=True, disturbance=0.5)
    assert r["reference_error_rad"] == pytest.approx(l["reference_error_rad"], abs=1e-12)
    assert r["final_phase_error_rad"] == pytest.approx(l["final_phase_error_rad"], abs=1e-12)
    assert r["payload_exact_match"] == l["payload_exact_match"]

def test_blind_readout_exposes_left_handed_coordinate_mismatch():
    r = run_trial(7, handedness=1, mode="no_history", orientation_aware=False, disturbance=0)
    l = run_trial(7, handedness=-1, mode="no_history", orientation_aware=False, disturbance=0)
    assert r["payload_exact_match"] is True
    assert l["payload_exact_match"] is False

def test_orientation_aware_readout_removes_mirror_coordinate_mismatch():
    for h in (-1, 1):
        result = run_trial(7, handedness=h, mode="no_history", orientation_aware=True, disturbance=0)
        assert result["payload_exact_match"] is True

def test_full_cycle_history_estimate_is_less_noisy_than_last_transition():
    full = run_trial(77, handedness=1, mode="full_cycle_history", disturbance=0.5)
    last = run_trial(77, handedness=1, mode="last_transition", disturbance=0.5)
    assert full["reference_error_rad"] < last["reference_error_rad"]

def test_factorial_experiment_reports_both_handednesses_and_readout_modes():
    result = run([11, 12], disturbances=(0.25,))
    assert len(result["summary"]) == 12
    assert "left/aware/full_cycle_history/d=0.25" in result["summary"]
    assert "right/blind/no_history/d=0.25" in result["summary"]

def test_reproducibility_and_input_validation():
    assert run([3, 4], disturbances=(0.5,)) == run([3, 4], disturbances=(0.5,))
    with pytest.raises(ValueError):
        run_trial(1, handedness=0, mode="full_cycle_history")
    with pytest.raises(ValueError):
        run_trial(1, handedness=1, mode="unknown")
