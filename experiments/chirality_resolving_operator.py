"""Candidate Hermitian operator that preserves signed torsion information.

The existing G5-like baseline uses |tau| in a symmetric ring Laplacian and
therefore cannot distinguish a helix from its mirror by spectrum. This
experiment adds a separate imaginary-skew channel built from signed torsion.

This is a mathematical/synthetic probe only. It does not alter production
Helix-Lock, establish a physical law, or claim payload recovery.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np


def ring_operators(kappa, tau, *, k_scale: float = 1.0,
                   kc_scale: float = 1.0, chirality_scale: float = 0.25):
    """Return (baseline, chiral, full) matrices for an oriented N-cycle.

    baseline = diag(k_scale*kappa) + kc_scale * L_cycle(|tau|)
    chiral   = i * chirality_scale * A_cycle(tau), A_cycle(tau)^T=-A_cycle(tau)
    full     = baseline + chiral

    Consequently full is Hermitian. Under mirror reflection tau -> -tau,
    baseline is unchanged and full -> conjugate(full).
    """
    kappa = np.asarray(kappa, dtype=float)
    tau = np.asarray(tau, dtype=float)
    if (kappa.ndim != 1 or tau.ndim != 1 or len(kappa) != len(tau)
            or len(kappa) < 3):
        raise ValueError("kappa and tau must be equal-length 1D arrays with N >= 3")
    if not np.all(np.isfinite(kappa)) or not np.all(np.isfinite(tau)):
        raise ValueError("kappa and tau must contain only finite values")
    if np.any(kappa < 0):
        raise ValueError("curvature values must be non-negative")
    if any(not math.isfinite(x) or x < 0 for x in
           (k_scale, kc_scale, chirality_scale)):
        raise ValueError("operator scales must be finite and non-negative")

    n = len(kappa)
    baseline = np.diag(k_scale * kappa)
    oriented = np.zeros((n, n), dtype=float)
    for i in range(n):
        j = (i + 1) % n
        weight = kc_scale * abs(tau[i])
        baseline[i, i] += weight
        baseline[j, j] += weight
        baseline[i, j] -= weight
        baseline[j, i] -= weight
        oriented[i, j] += tau[i]
        oriented[j, i] -= tau[i]

    chiral = 1j * chirality_scale * oriented
    full = baseline.astype(complex) + chiral
    return baseline, chiral, full


def chirality_probe(chiral, mode: int = 1) -> float:
    """Signed response of a fixed complex Fourier probe to the chiral channel."""
    n = chiral.shape[0]
    if not 0 < mode < n:
        raise ValueError("mode must be between 1 and N-1")
    q = np.exp(2j * np.pi * mode * np.arange(n) / n) / math.sqrt(n)
    return float(np.vdot(q, chiral @ q).real)



def reverse_cycle_orientation(kappa, tau):
    """Reindex the same oriented ring in the opposite traversal direction."""
    kappa = np.asarray(kappa, dtype=float)
    tau = np.asarray(tau, dtype=float)
    if kappa.ndim != 1 or tau.ndim != 1 or len(kappa) != len(tau) or len(kappa) < 3:
        raise ValueError("kappa and tau must be equal-length 1D arrays with N >= 3")
    n = len(kappa)
    indices = (-np.arange(n)) % n
    reversed_kappa = kappa[indices]
    reversed_tau = -tau[(-np.arange(n) - 1) % n]
    return reversed_kappa, reversed_tau


def real_doubled_representation(operator):
    """Represent a Hermitian complex matrix as an equivalent real symmetric matrix."""
    operator = np.asarray(operator, dtype=complex)
    if operator.ndim != 2 or operator.shape[0] != operator.shape[1]:
        raise ValueError("operator must be square")
    if not np.allclose(operator, operator.conj().T, atol=1e-12, rtol=0):
        raise ValueError("operator must be Hermitian")
    real = operator.real
    imag = operator.imag
    return np.block([[real, -imag], [imag, real]])


def run(samples: int = 128, radius: float = 1.0,
        pitch_parameter: float = 0.35, chirality_scale: float = 0.25) -> dict:
    if samples < 8:
        raise ValueError("samples must be >= 8")
    if radius <= 0 or pitch_parameter <= 0:
        raise ValueError("radius and pitch_parameter must be positive")

    speed_sq = radius * radius + pitch_parameter * pitch_parameter
    curvature = radius / speed_sq
    torsion = pitch_parameter / speed_sq
    kappa_r = np.full(samples, curvature)
    tau_r = np.full(samples, torsion)
    tau_l = -tau_r

    base_r, chiral_r, full_r = ring_operators(
        kappa_r, tau_r, chirality_scale=chirality_scale
    )
    base_l, chiral_l, full_l = ring_operators(
        kappa_r, tau_l, chirality_scale=chirality_scale
    )
    eig_r = np.linalg.eigvalsh(full_r)
    eig_l = np.linalg.eigvalsh(full_l)

    return {
        "status": "candidate_operator_synthetic_geometry_only",
        "operator": "H = diag(kappa) + L_cycle(abs(tau)) + i*gamma*A_cycle(tau)",
        "samples": samples,
        "radius": radius,
        "pitch_parameter": pitch_parameter,
        "chirality_scale": chirality_scale,
        "right_torsion": torsion,
        "left_torsion": -torsion,
        "baseline_equal_under_mirror": bool(np.allclose(base_r, base_l)),
        "full_operator_mirror_conjugate": bool(
            np.allclose(full_l, np.conjugate(full_r), atol=1e-12, rtol=0)
        ),
        "right_operator_hermitian": bool(
            np.allclose(full_r, full_r.conj().T, atol=1e-12, rtol=0)
        ),
        "mirror_spectra_equal": bool(
            np.allclose(eig_r, eig_l, atol=1e-12, rtol=0)
        ),
        "minimum_eigenvalue_right": float(eig_r.min()),
        "minimum_eigenvalue_left": float(eig_l.min()),
        "right_chiral_probe": chirality_probe(chiral_r),
        "left_chiral_probe": chirality_probe(chiral_l),
        "chiral_probe_sign_reverses": bool(
            chirality_probe(chiral_r) * chirality_probe(chiral_l) < 0
        ),
        "interpretation_limits": [
            "The imaginary-skew term is a candidate extension, not an established TIMDR axiom.",
            "Equal spectra under mirror conjugation do not mean the operators are identical.",
            "The signed probe response distinguishes orientation for the selected mode; it is not a payload-recovery metric.",
            "Positive semidefiniteness and physical meaning must be established for the intended application.",
            "This experiment does not modify the production G5 construction or cryptographic paths.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--samples", type=int, default=128)
    args = parser.parse_args()
    result = run(samples=args.samples)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
