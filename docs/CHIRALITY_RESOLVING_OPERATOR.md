# Candidate chirality-resolving operator

**Status:** isolated mathematical experiment; not a production change and not a TIMDR axiom.

## Motivation

The existing synthetic G5 ring construction uses the edge weight `|tau|` in a symmetric cycle Laplacian. A mirror transformation reverses torsion, `tau -> -tau`, but leaves `|tau|` unchanged. The baseline operator therefore discards handedness.

## Candidate construction

For an oriented N-cycle, define:

- `L_abs(tau)`: the ordinary symmetric cycle Laplacian with edge weights `|tau_i|`;
- `A(tau)`: an oriented, real skew-symmetric cycle matrix, with `A[i,i+1] += tau_i` and `A[i+1,i] -= tau_i`;
- `H(tau) = diag(kappa) + L_abs(tau) + i gamma A(tau)`, where `gamma >= 0`.

Since `A^T = -A`, the matrix `i A` is Hermitian. Under a mirror operation:

`H(-tau) = conjugate(H(tau))`.

Therefore the mirror pair has the same real eigenvalue spectrum, while the complex operator and its phase-sensitive responses retain an orientation sign. Spectral invariance does not require erasing chirality from the operator itself.

A fixed complex Fourier probe `q_m[j] = exp(2 pi i m j/N)/sqrt(N)` reads the signed chiral channel through `Re(q_m* (i gamma A) q_m)`. For a uniform nonzero torsion ring and nontrivial mode, this response reverses sign when torsion reverses.

## What this establishes — and what it does not

The experiment can establish algebraic properties of this proposed finite-dimensional construction: Hermiticity, mirror-conjugation covariance, equal mirror spectra, and sign reversal of a selected chiral probe.

It does not establish that this is the unique extension, that `gamma` has a physically justified value, that the operator is the correct TIMDR G5 operator, or that it reconstructs a signal or payload. Positive semidefiniteness and dimensional consistency must be checked for the intended application. The term is kept outside production code and existing axioms.

## Reproduction

Run:

`python -m experiments.chirality_resolving_operator --output chirality-resolving-operator.json`

Tests:

`pytest -q tests/test_chirality_resolving_operator.py`

## Next falsification steps

1. Sweep nonuniform signed torsion profiles, including sign changes along the ring.
2. Test orientation reversal together with reversal of cycle indexing; these are distinct transformations and must not be conflated.
3. Check eigenvalue bounds as `gamma` increases and identify conditions for positive semidefiniteness.
4. Compare the complex operator against a real doubled-state representation, so the result does not depend on complex-number conventions.
5. Only after those checks, consider whether a corresponding term has a defensible geometric derivation in TIMDR.
