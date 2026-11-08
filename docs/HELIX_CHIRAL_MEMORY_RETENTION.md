# Helix handedness and information-memory retention

**Status:** synthetic factorial experiment; not production dynamics or a physical claim.

## Research question

Does a left- versus right-handed helix intrinsically change retention of encoded information, or does an apparent difference arise because the same phase code is read in mirrored local coordinate systems?

## Factorial design

Crossed variables:
- handedness: left (-1), right (+1);
- memory: no history, last transition, full-cycle history;
- readout: orientation-blind or orientation-aware;
- disturbance: 0.25, 0.5, 0.85, 1.2 rad.

Two relative-phase symbols are selected from a four-angle codebook. Local phase is defined as `phi_local = handedness * phi_canonical`. The orientation-aware path multiplies by handedness before storing and reading canonical information. Mirror-paired trials reuse identical canonical random perturbations.

The last-transition mode stores one history sample. Full-cycle history uses a circular mean over complete cycles. An explicit reference-feedback law attempts recovery after a phase disturbance; no-history applies no feedback.

## Interpretation

1. A blind left-handed readout may decode a mirrored phase code incorrectly even if no information was lost.
2. Reference-estimation error compares one-sample memory with full-cycle averaging.
3. Under the mirror-covariant null model, left/right trials with orientation-aware readout should match exactly. A gap indicates an implementation or covariance failure, not a physical discovery.

## Limits

- Synthetic phase-memory toy model, not production Helix-Lock, GIA-TIMDR, or TSI.
- Orientation normalization is a coordinate convention, not a physical law.
- Feedback is imposed by the experiment, not derived from Chronoprocess.
- Payload is a two-symbol phase code, not arbitrary data or ciphertext.
- Intrinsic chirality dependence requires a justified handedness-dependent storage/noise mechanism.

## Reproduction

`python -m experiments.helix_chiral_memory_retention --output helix-chiral-memory-retention.json`

`pytest -q tests/test_helix_chiral_memory_retention.py`

## Next falsification steps

1. Verify exact paired left/right equality under the orientation-aware null model.
2. Add handedness-dependent noise/coupling only after deriving it from a stated geometric/dynamical hypothesis.
3. Measure information before and after disturbance, not only phase coherence.
4. Add larger codebooks and payload lengths.
5. Compare against a non-helical control with identical noise and feedback.
