"""Chirality-aware signal mapping on a geometric helical tunnel.

Synthetic geometry experiment only. It tests mirror covariance of a signal
laid on a Frenet frame and exposes the chirality information discarded by
the current G5 |torsion| coupling. It is not a production TIMDR model.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - gives a useful CLI error
    raise RuntimeError("This experiment requires numpy") from exc


def wrap(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def helix_frame(t: float, *, radius: float = 1.0, pitch_parameter: float = 0.35, handedness: int = 1):
    """Return position and Frenet T,N,B for r=(a cos t,a sin t,h t)."""
    if radius <= 0 or pitch_parameter <= 0:
        raise ValueError("radius and pitch_parameter must be positive")
    if handedness not in (-1, 1):
        raise ValueError("handedness must be -1 (left) or +1 (right)")
    h = handedness * pitch_parameter
    speed = math.sqrt(radius * radius + h * h)
    position = (radius * math.cos(t), radius * math.sin(t), h * t)
    tangent = (-radius * math.sin(t) / speed, radius * math.cos(t) / speed, h / speed)
    normal = (-math.cos(t), -math.sin(t), 0.0)
    binormal = (h * math.sin(t) / speed, -h * math.cos(t) / speed, radius / speed)
    curvature = radius / (radius * radius + h * h)
    torsion = h / (radius * radius + h * h)
    return position, tangent, normal, binormal, curvature, torsion


def dot(a, b) -> float:
    return sum(x * y for x, y in zip(a, b))


def laid_signal(t: float, *, handedness: int, phase_rate: float = 1.7,
                radius: float = 1.0, pitch_parameter: float = 0.35,
                chirality_aware: bool = True):
    """Unit transverse signal vector; phase direction follows tunnel chirality."""
    _, _, normal, binormal, _, _ = helix_frame(
        t, radius=radius, pitch_parameter=pitch_parameter, handedness=handedness
    )
    phase_sign = handedness if chirality_aware else 1
    phase = phase_sign * phase_rate * t
    return tuple(math.cos(phase) * normal[i] + math.sin(phase) * binormal[i] for i in range(3))


def g5_ring_stiffness(kappa, tau, *, k_scale=1.0, kc_scale=1.0):
    """Mirror of current G5 construction: edge coupling uses abs(tau)."""
    kappa = np.asarray(kappa, dtype=float)
    tau = np.asarray(tau, dtype=float)
    if kappa.ndim != 1 or tau.ndim != 1 or len(kappa) != len(tau) or len(kappa) < 3:
        raise ValueError("kappa and tau must be equal-length 1D arrays with N >= 3")
    n = len(kappa)
    stiffness = np.diag(k_scale * kappa)
    for i in range(n):
        j = (i + 1) % n
        edge = kc_scale * abs(tau[i])
        stiffness[i, i] += edge
        stiffness[j, j] += edge
        stiffness[i, j] -= edge
        stiffness[j, i] -= edge
    return stiffness


def run(samples: int = 256, turns: float = 3.0, radius: float = 1.0,
        pitch_parameter: float = 0.35, phase_rate: float = 1.7) -> dict:
    if samples < 16 or turns <= 0:
        raise ValueError("samples must be >= 16 and turns must be positive")
    ts = [2.0 * math.pi * turns * i / (samples - 1) for i in range(samples)]
    right = [helix_frame(t, radius=radius, pitch_parameter=pitch_parameter, handedness=1) for t in ts]
    left = [helix_frame(t, radius=radius, pitch_parameter=pitch_parameter, handedness=-1) for t in ts]
    # Reflection through z=0 maps the right-handed tunnel to the left-handed one.
    reflect = lambda v: (v[0], v[1], -v[2])
    right_signal_aligned = [laid_signal(t, handedness=1, phase_rate=phase_rate, radius=radius, pitch_parameter=pitch_parameter, chirality_aware=True) for t in ts]
    left_signal_aligned = [laid_signal(t, handedness=-1, phase_rate=phase_rate, radius=radius, pitch_parameter=pitch_parameter, chirality_aware=True) for t in ts]
    left_signal_naive = [laid_signal(t, handedness=-1, phase_rate=phase_rate, radius=radius, pitch_parameter=pitch_parameter, chirality_aware=False) for t in ts]
    aligned_errors = [math.sqrt(sum((reflect(a)[j] - b[j]) ** 2 for j in range(3))) for a, b in zip(right_signal_aligned, left_signal_aligned)]
    naive_errors = [math.sqrt(sum((reflect(a)[j] - b[j]) ** 2 for j in range(3))) for a, b in zip(right_signal_aligned, left_signal_naive)]
    kappa_r = [row[4] for row in right]
    tau_r = [row[5] for row in right]
    kappa_l = [row[4] for row in left]
    tau_l = [row[5] for row in left]
    K_r = g5_ring_stiffness(kappa_r, tau_r)
    K_l = g5_ring_stiffness(kappa_l, tau_l)
    eig_r = np.linalg.eigvalsh(K_r)
    eig_l = np.linalg.eigvalsh(K_l)
    return {
        "status": "synthetic_geometry_experiment_only",
        "geometry": "r(t)=(a*cos(t), a*sin(t), handedness*h*t)",
        "samples": samples, "turns": turns, "radius": radius,
        "pitch_parameter": pitch_parameter, "phase_rate": phase_rate,
        "right_handed_torsion": round(tau_r[0], 12),
        "left_handed_torsion": round(tau_l[0], 12),
        "max_curvature_pair_difference": round(max(abs(a-b) for a,b in zip(kappa_r,kappa_l)), 12),
        "max_torsion_sign_pair_error": round(max(abs(a+b) for a,b in zip(tau_r,tau_l)), 12),
        "mirror_signal_error_chirality_aware": round(max(aligned_errors), 12),
        "mean_mirror_signal_error_chirality_aware": round(sum(aligned_errors)/len(aligned_errors), 12),
        "mirror_signal_error_naive_same_phase_sign": round(max(naive_errors), 12),
        "mean_mirror_signal_error_naive_same_phase_sign": round(sum(naive_errors)/len(naive_errors), 12),
        "g5_stiffness_matrices_equal_under_mirror": bool(np.allclose(K_r, K_l, atol=1e-12, rtol=0)),
        "g5_spectrum_equal_under_mirror": bool(np.allclose(eig_r, eig_l, atol=1e-12, rtol=0)),
        "g5_min_eigenvalue": round(float(min(eig_r.min(), eig_l.min())), 12),
        "interpretation_limits": [
            "The helix and signal are analytic synthetic constructions, not the original TIMDR signal representation.",
            "The phase-sign rule is a candidate mirror-covariant convention, not yet derived from TSI.",
            "Equal G5 spectra occur because current G5 replaces torsion by abs(tau); this does not prove physical equivalence.",
            "The test measures geometric signal-vector covariance, not recovery of arbitrary payload or cryptographic data.",
            "The current experiment uses an ideal Frenet frame; production code needs robust frame transport near low-curvature regions.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--samples", type=int, default=256)
    args = parser.parse_args()
    result = run(samples=args.samples)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
