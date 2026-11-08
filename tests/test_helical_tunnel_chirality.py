import pytest

from experiments.helical_tunnel_chirality import helix_frame, laid_signal, run


def test_mirror_helix_preserves_curvature_and_reverses_torsion_sign():
    right = helix_frame(0.7, handedness=1)
    left = helix_frame(0.7, handedness=-1)
    assert right[4] == pytest.approx(left[4], abs=1e-12)
    assert right[5] == pytest.approx(-left[5], abs=1e-12)


def test_chirality_aware_signal_is_covariant_under_mirror_reflection():
    result = run(samples=128)
    assert result["mirror_signal_error_chirality_aware"] < 1e-10
    assert result["mean_mirror_signal_error_chirality_aware"] < 1e-10


def test_naive_same_phase_sign_does_not_follow_mirror_orientation():
    result = run(samples=128)
    assert result["mean_mirror_signal_error_naive_same_phase_sign"] > 0.1


def test_current_g5_abs_torsion_discards_chirality_in_spectrum():
    result = run(samples=128)
    assert result["g5_stiffness_matrices_equal_under_mirror"] is True
    assert result["g5_spectrum_equal_under_mirror"] is True


def test_chirality_experiment_is_reproducible_and_validates_inputs():
    assert run(samples=64) == run(samples=64)
    with pytest.raises(ValueError):
        run(samples=8)
    with pytest.raises(ValueError):
        helix_frame(0.0, handedness=0)


def test_signal_vector_is_transverse_to_tunnel_tangent():
    t = 1.3
    _, tangent, _, _, _, _ = helix_frame(t, handedness=-1)
    signal = laid_signal(t, handedness=-1)
    assert sum(a*b for a,b in zip(tangent, signal)) == pytest.approx(0.0, abs=1e-12)
