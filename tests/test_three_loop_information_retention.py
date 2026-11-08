from experiments.three_loop_information_retention import run, run_trial


def test_full_cycle_history_estimate_is_less_noisy_than_last_transition():
    full = run_trial(77, mode="full_cycle_history", amplitude=0.5)
    last = run_trial(77, mode="last_transition", amplitude=0.5)
    assert full["reference_error_rad"] < last["reference_error_rad"]


def test_history_feedback_recovers_encoded_phase_payload_in_low_disturbance_case():
    full = run_trial(1234, mode="full_cycle_history", amplitude=0.25)
    assert full["payload_exact_match"] is True
    assert full["final_phase_error_rad"] < 0.05


def test_no_history_does_not_secretly_apply_feedback():
    no_history = run_trial(321, mode="no_history", amplitude=0.85)
    assert no_history["reference_error_rad"] is None


def test_information_experiment_reports_coherence_and_payload_separately():
    result = run([1001, 1002], amplitudes=(0.1, 0.85))
    row = result["summary"]["full_cycle_history@0.1"]
    assert "mean_order_parameter" in row
    assert "payload_exact_match_rate" in row
    assert row["trials"] == 2


def test_experiment_is_reproducible_for_fixed_seeds():
    a = run([8, 9], amplitudes=(0.1,))
    b = run([8, 9], amplitudes=(0.1,))
    assert a == b
