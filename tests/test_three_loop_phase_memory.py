import pytest

from experiments.three_loop_phase_memory import run, run_trial


def test_three_loop_memory_reduces_phase_error_in_declared_synthetic_model():
    result = run(range(100, 120))
    errors = result["mean_post_disturbance_phase_error"]
    assert errors["coupling_plus_memory"] < errors["coupling_only"]
    assert errors["coupling_only"] < errors["no_memory_no_coupling"]


def test_phase_memory_experiment_is_reproducible():
    first = run(range(100, 105))
    second = run(range(100, 105))
    assert first == second


def test_memory_feedback_is_explicitly_separate_from_phase_coupling():
    plain = run_trial(101, mode="coupling_only")
    memory = run_trial(101, mode="coupling_plus_memory")
    assert plain["mode"] == "coupling_only"
    assert memory["mode"] == "coupling_plus_memory"
    assert memory["post_disturbance_mean_phase_error"] < plain["post_disturbance_mean_phase_error"]
    assert memory["disturbance_steps"] == plain["disturbance_steps"]



def test_equal_common_mode_disturbance_preserves_relative_phase_without_repair():
    result = run_trial(
        202,
        mode="no_memory_no_coupling",
        disturbance_targets=(0, 1, 2),
    )
    # Equal frequency offsets move all phases together; relative phase should
    # remain close to its initial value apart from the small independent noise.
    assert result["post_disturbance_mean_phase_error"] < 0.01
    assert result["disturbance_targets"] == [0, 1, 2]


def test_disturbance_target_indices_are_validated():
    with pytest.raises(ValueError, match="loop indices"):
        run_trial(
            203,
            mode="coupling_only",
            disturbance_targets=(3,),
        )



def test_stale_reference_feedback_opposes_a_legitimate_phase_transition():
    from experiments.three_loop_phase_memory import reference_feedback_correction

    stored_reference = 0.7
    legitimate_new_phase = 1.1
    correction = reference_feedback_correction(
        legitimate_new_phase,
        stored_reference,
        gain=0.2,
    )
    assert correction < 0
    assert correction * (legitimate_new_phase - stored_reference) < 0


def test_seed_generators_are_reused_consistently_across_modes():
    result = run(iter([11, 12, 13]))
    assert result["trial_count_per_mode"] == 3
    assert result["seed_values"] == [11, 12, 13]
    assert all(len(trials) == 3 for trials in result["trials"].values())
