# TSI → Helix development directive (2026-11-08)

## User's architectural decision

**We are building Helix for TSI.** The chirality/phase experiments are intended to become useful intelligent properties of Helix, not standalone demonstrations. Keep this as a durable design directive for future sessions.

## Intended capabilities

1. **Signal fingerprinting:** estimate phase, winding/handedness, stability and temporal changes; compare with stored patterns.
2. **Directional memory:** retain the orientation convention, phase history and changes in chirality alongside payload observations.
3. **Adaptive decoding:** compare hypotheses under noise, phase drift and opposite-winding reflections; select with calibrated confidence.
4. **Anomaly detection:** flag unexpected reversals, phase inconsistencies and reflection-like signatures; avoid overclaiming authentication.
5. **Uncertainty-aware behavior:** abstain or request additional evidence when orientation cannot be identified or confidence is low.

## Existing experimental starting point

- `experiments/helix_chiral_memory_inference.py`: infer handedness changes from phase history; absolute sign has global mirror ambiguity without an anchor.
- `experiments/helix_chiral_signal.py`: QPSK payload and signed angular phase winding, angular receiver-array decoding.
- `experiments/helix_chiral_signal_channel.py`: shared phase drift (single-snapshot Doppler proxy) and coherent opposite-winding echo.
- `docs/HELIX_CHIRAL_SIGNAL.md` and `docs/HELIX_CHIRAL_SIGNAL_CHANNEL.md`: experiment definitions and limitations.
- CI after fixing duplicate zero-drift calibration cases: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42507962322 (Python 3.11 and 3.12 succeeded).

## Next implementation sequence

1. Add an isolated `HelixChiralIntelligence` prototype, **not** changing production Helix-Lock/AIRP or cryptographic trust decisions.
2. Define typed input/output contract: angular phase samples, timestamps, reference orientation, optional pilot; output chirality probabilities, payload candidate, anomaly score, calibration/ambiguity status.
3. Add short-term phase-history memory and a hypothesis bank for direct path, reflection, and reversal. Separate *unknown* from confident right/left.
4. Benchmark across noise, narrow sensor aperture, source motion, time-varying Doppler, multipath and adversarially misleading reflections. Include mirrored and no-anchor controls.
5. Promote into Helix/TSI integration only if metrics beat a simple baseline on held-out synthetic and, eventually, real measurements.

## Scientific and safety boundaries

Helical *phase structure* is not proof that every natural signal travels along a helix. Handedness depends on a defined oriented axis and measurement frame. A signal's chirality alone is **not authentication**, physical identity, or cryptographic evidence. Existing Helix-Lock security behavior stays unchanged unless independently validated and explicitly approved.

## Continuation instruction

When the user says to continue work on Helix for TSI, start here, inspect current CI and the experimental branch, implement the next isolated intelligence module, run negative controls, and update both repositories' checkpoints with confirmed results. Do not treat earlier synthetic success as physical validation of TSI.
