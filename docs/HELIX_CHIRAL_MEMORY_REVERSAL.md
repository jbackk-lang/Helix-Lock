# Mid-history handedness reversal

This follow-up synthetic test deliberately changes the sign of the local phase coordinate at a chosen history boundary, while holding the canonical two-symbol payload fixed. The aim is to falsify an apparent loss-of-memory interpretation by distinguishing per-sample handedness normalization from applying only the final handedness to the entire history.

## Controls

- Five flip boundaries: 0, 3, 6, 9, 12 of 12 cycles.
- Two initial handedness signs.
- Three readout strategies: per-sample handedness labels; final-only handedness; blind local-phase averaging.
- 100 paired random seeds; fixed canonical disturbance.
- Exact payload recovery, circular reference error, final phase error.

The per-sample method is given correct handedness labels, so this is a decoder control rather than evidence of intrinsic physical memory. Final-only is correct if no handedness reversal occurs; at a reversal it mixes incompatible phase coordinate conventions.

Run:
`python -m experiments.helix_chiral_memory_reversal --output helix-chiral-memory-reversal.json`

Test:
`pytest -q tests/test_helix_chiral_memory_reversal.py`

No production cipher or G5 axioms are changed.
