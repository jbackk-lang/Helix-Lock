import numpy as np
import pytest

from experiments.chirality_resolving_operator import (
    chirality_probe,
    ring_operators,
    run,
)


def test_full_operator_is_hermitian():
    kappa = np.full(16, 0.8)
    tau = np.full(16, 0.3)
    _, _, operator = ring_operators(kappa, tau)
    assert np.allclose(operator, operator.conj().T, atol=1e-12)


def test_mirror_changes_operator_by_complex_conjugation():
    kappa = np.full(16, 0.8)
    tau = np.full(16, 0.3)
    _, _, right = ring_operators(kappa, tau)
    _, _, left = ring_operators(kappa, -tau)
    assert np.allclose(left, right.conj(), atol=1e-12)


def test_mirror_preserves_spectrum_but_reverses_signed_probe():
    result = run(samples=32)
    assert result["baseline_equal_under_mirror"] is True
    assert result["full_operator_mirror_conjugate"] is True
    assert result["right_operator_hermitian"] is True
    assert result["mirror_spectra_equal"] is True
    assert result["chiral_probe_sign_reverses"] is True
    assert result["right_chiral_probe"] == pytest.approx(
        -result["left_chiral_probe"], abs=1e-12
    )
    assert abs(result["right_chiral_probe"]) > 1e-6


def test_zero_chirality_scale_recovers_baseline_operator():
    kappa = np.full(12, 0.7)
    tau = np.full(12, 0.2)
    baseline, chiral, full = ring_operators(
        kappa, tau, chirality_scale=0.0
    )
    assert np.allclose(chiral, 0.0)
    assert np.allclose(full, baseline)


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        ring_operators([1.0, 1.0], [0.2, 0.2])
    with pytest.raises(ValueError):
        ring_operators([1.0, -0.1, 1.0], [0.2, 0.2, 0.2])
    with pytest.raises(ValueError):
        chirality_probe(np.zeros((8, 8)), mode=8)
    with pytest.raises(ValueError):
        run(samples=4)
