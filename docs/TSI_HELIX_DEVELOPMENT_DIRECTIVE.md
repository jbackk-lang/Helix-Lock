# Helix autonomous development directive (corrected 2026-11-08)

## Current user decision — overrides the earlier TSI directive

**We are developing Helix for Helix itself, NOT for TSI at this stage.** TSI work is deferred until access to TSI becomes available. Do not interpret helical signal experiments as TSI integration requirements. The previous directive that Helix was being built for TSI was explicitly corrected by the user.

## Helix capabilities to develop now

1. Signal fingerprinting: phase, winding, stability, temporal changes and pattern comparisons.
2. Directional memory: record orientation conventions, phase history and changes in handedness.
3. Adaptive decoding: compare direct-path, reflection and reversal hypotheses under noise and drift.
4. Anomaly detection: flag inconsistent phase, abrupt reversals and suspicious echoes without treating chirality as authentication.
5. Uncertainty-aware behavior: report ambiguity and abstain from unsupported decisions.

## Experimental baseline

- `experiments/helix_chiral_memory_inference.py`: phase-history inference, including absolute-sign ambiguity without an anchor.
- `experiments/helix_chiral_signal.py`: signed angular phase and QPSK payload decoding.
- `experiments/helix_chiral_signal_channel.py`: phase-drift and opposite-winding echo controls.
- CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42507962322 passed on Python 3.11 and 3.12.

## Immediate implementation plan

Build an **isolated HelixChiralIntelligence prototype within Helix**, with typed inputs/outputs, confidence/ambiguity status, temporal memory, and negative controls. Keep production Helix-Lock/AIRP and cryptographic security behavior unchanged until independently validated. Test against simple baselines under noise, reflections, Doppler-like time evolution, mirror reversal and missing orientation anchors.

## TSI status

**Deferred.** Revisit TSI only when access is available and the user explicitly resumes that work. Do not present current Helix research as an implementation of TSI.

## Scientific boundary

A helical spatial phase pattern does not establish that all natural signals follow helical trajectories. Handedness is defined relative to an oriented reference. Synthetic simulation success is not empirical validation. Chirality alone does not authenticate an origin.

## Continuation instruction

When resuming, prioritize **Helix-for-Helix** engineering and validation. Read this correction first. Keep both repositories' checkpoints aligned, but do not start TSI integration without access and renewed direction.
