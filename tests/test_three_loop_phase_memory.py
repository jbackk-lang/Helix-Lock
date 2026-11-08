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
