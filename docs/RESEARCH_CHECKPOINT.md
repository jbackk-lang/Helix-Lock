# RESEARCH_CHECKPOINT — Helix-Lock (2026-11-08)

## Purpose and restart instructions

This is a durable handoff for any future session after a context reset. **Read this file and inspect the current branch, PRs, GitHub Actions logs and source before making claims or changes.** Do not assume the chat history is complete.

Research scope: chirality-resolving Hermitian ring operator; synthetic phase-memory retention with mirrored left/right helix coordinates. Do not conflate synthetic results with established GIA-TIMDR/TSI physics or production encryption.

## Active work

- PR #1: https://github.com/jbackk-lang/Helix-Lock/pull/1 (branch `experiment/chirality-resolving-operator`, base `main`)
- PR #2: https://github.com/jbackk-lang/Helix-Lock/pull/2 (branch `experiment/chiral-memory-retention`, base `experiment/chirality-resolving-operator`)
- GIA-TIMDR companion PR: https://github.com/jbackk-lang/GIA-TIMDR/pull/2
- Last known successful new-experiment CI: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42505701203 (163 passed on Python 3.11 and 3.12)
- Last known successful base-operator CI: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42505801696

PRs are drafts, not merged. Re-check their current state before proceeding.

## Error classification — verified evidence

1. Earlier chirality-operator CI failure: missing exported helper functions `reverse_cycle_orientation` and `real_doubled_representation` referenced by tests, and missing test imports. This was an **actual implementation/test integration defect**, not evidence that geometry or chirality hypothesis failed. Fixed on both the operator branch and the child experiment branch. CI on the operator branch passed after correction.
2. Earlier memory-test CI failure: assertion `full_history_error < last_transition_error` for a **single seed 77** failed (0.04219716 vs 0.01762866). The assertion was scientifically overstrong: averaging independent noise reduces error in expectation, not for every individual draw. Replaced with a paired 100-seed mean comparison. CI passed. **This was a test/assumption error, not proof of broken memory code.**
3. A malformed JSON output newline was corrected in the experiment module. Treat as an implementation defect.
4. Whether any of these defects arose from an earlier conversation reset is **unknown**. No evidence can distinguish that cause; do not attribute code defects to missing model context without repository/log proof.

## Synthetic experiment results (100 seeds per cell)

For orientation-aware readout and full-cycle history, left and right have identical mean phase error 0.01894574 rad and 100% exact two-symbol payload recovery for all tested disturbances (0.25, 0.5, 0.85, 1.2 rad).
At disturbance 0.85 rad: orientation-aware no-history recovery 7%; last-transition history 100%; full-cycle history 100% (both handednesses).
Orientation-blind left-handed full-cycle recovery 0% for the four disturbances, whereas orientation-blind right-handed full-cycle recovery is 100%. This is a *coordinate-convention decoding mismatch*, not intrinsic information loss.
Mean reference estimation error: full-cycle 0.01900644 rad, last transition 0.06421710 rad (both handednesses after orientation normalization).

The controller is explicitly given a stored reference. Thus perfect recovery under these conditions does not demonstrate spontaneous memory or physical self-repair.

## Next experiment

Test a **mid-history handedness reversal** and distinguish:
- fixed canonical payload, local phase sign flips;
- memory/history collected before vs after reversal;
- decoder with and without chirality labels for each sample;
- no-history, last-transition and full-cycle history controls;
- matched non-helical baseline, if meaningful.

Report payload accuracy and circular reference error; add tests for mirror covariance, reversal boundaries, and zero-disturbance controls. The synthetic model has no justified intrinsic handedness-dependent storage law. Never introduce one without explicitly labeling it a new hypothesis.

## Workflow

Commit code, tests, report-generation changes and handoff notes to named research branches. Run GitHub Actions on Python 3.11/3.12; inspect failing logs and isolate test versus implementation versus theory mistakes. Keep PRs draft until verified. Never merge into `main` merely to preserve progress.

## Continuation: mid-history reversal experiment

Added `experiments/helix_chiral_memory_reversal.py`, `tests/test_helix_chiral_memory_reversal.py`, `docs/HELIX_CHIRAL_MEMORY_REVERSAL.md` and CI report upload on the same research branch. Commit enabling CI: `73fc70c9a84b31f673886499724a7759bc8a1584`. CI run: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42505958517 . **Do not assume success until the run is checked.** This models a change of local coordinate sign during history acquisition, not a physical helix reversal.

## Verified CI and new negative control (2026-11-08 17:39+ UTC)

Reversal CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42505958517 **passed**, 177 tests on Python 3.11 and 3.12. Midpoint flip (6 of 12 cycles), 100 seeds: per-sample orientation-aware readout 100% exact payload recovery, mean reference error 0.01900644 rad. This is synthetic, and the correct per-sample labels are supplied.

Added `shuffled_labels` negative control, which preserves the left/right label counts but destroys their sample alignment. Code commit `e493b6adcf826a36887d65df7046f73d818063b1`, tests commit `26088bcd779e8883805fa9c7e47aba837e8aecfa`. New CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42506116845 **pending at time of checkpoint**. Do not claim pass before checking it.

## 2026-11-08 17:41+ UTC — chirality inference without per-sample labels

Shuffled-label control passed CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42506116845 : **179 tests passed on both Python 3.11 and 3.12**. For midpoint flip (6/12), start=+1, 100 seeds: correct per-sample labels 100% exact payload, reference error 0.01900644 rad; final-only labels 5%, 0.85110901 rad; shuffled labels 5%, 0.93366167 rad. These are synthetic readout errors, not physical memory loss.

New `experiments/helix_chiral_memory_inference.py`, `tests/test_helix_chiral_memory_inference.py`, `docs/HELIX_CHIRAL_MEMORY_INFERENCE.md` and CI workflow changes at commit `cd5a33322fea432021b78084ed27ddd4e82ac308`. CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42506276081 was **pending at checkpoint**. The decoder uses a Viterbi phase-continuity criterion and optionally knows ONLY the first sample's handedness, not all labels or flip location. Crucial: without an orientation anchor, absolute handedness and canonical payload are non-identifiable due to global sign symmetry; modulo-global-sign accuracy is reported separately. Do not claim physical chirality sensing.

## 2026-11-08 17:42+ UTC — inference CI PASS and interpretation warning

CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42506276081 passed **183 tests** on both Python 3.11 and 3.12. At midpoint flip (6/12), noise 0.08 rad, 100 seeds: anchored inferred labels 100% correct, exact payload recovery 100%, phase error 0.01900645 rad. At noise 0.4 rad: anchored mean label accuracy 93.25%, payload recovery 92%, phase error 0.13252048 rad.

**Important caution:** The unanchored variant also reports 100% absolute label accuracy for the particular start=+1 benchmark at noise 0.08. This is NOT evidence that the global sign was inferred: the Viterbi tie-breaking picks a deterministic sign. The globally mirrored latent explanation produces identical observations. The appropriate metric is accuracy modulo global sign, and an external anchor is required to identify canonical payload sign. Added mirror-pair identifiability tests in commit `ceaa942d16695b3bcb67eed3549c4aa7c03f50b2`; CI must be rechecked.

## 2026-11-08 17:54+ UTC — synthetic helical signal transmission

Added `experiments/helix_chiral_signal.py`, `tests/test_helix_chiral_signal.py`, and `docs/HELIX_CHIRAL_SIGNAL.md` on the draft research branch. Model: angular phase `m*theta + QPSK_payload_phase + common_offset + Gaussian_noise`, with winding m=+/-1. Receiver jointly decodes chirality and payload from a ring of angular samples. Explicit controls: 1/2/4/12 receivers, angular aperture, noise, unknown/calibrated phase offset, mirror reflection.

Local independent prototype (200 deterministic seeds, 0.12 rad noise) gave 12-sensor calibrated joint accuracy 100%; 1-sensor chirality accuracy 49.5% with score-margin zero; 12-sensor uncalibrated quarter-turn phase offset chirality 100% but payload 0%. These are *prototype outputs*, not yet GitHub CI results. New CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42507351434 pending when checkpoint written. Source/test commit `f46a2a17c8d6d91e5a4b013b17d637755e6d0789`, CI commit `89c718db01fb2c7ce07af92eb1df6d9f75e783b5`.

Important: a helical spatial phase profile is not a claim that all natural signals form helical trajectories, and this synthetic model has no channel dynamics.

## 2026-11-08 17:59+ UTC — phase drift and coherent reflection

Helix-Lock adds `experiments/helix_chiral_signal_channel.py`, `tests/test_helix_chiral_signal_channel.py`, `docs/HELIX_CHIRAL_SIGNAL_CHANNEL.md`. Synthetic common phase drift (single-snapshot Doppler proxy) and opposite-winding coherent echo with amplitudes 0/0.3/0.8/1.2. A strong reflected field can invert decoded winding. CI run https://github.com/jbackk-lang/Helix-Lock/actions/runs/42507707647 was pending at checkpoint. Previous phase-signal CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42507351434 completed successfully on Python 3.11 and 3.12. No empirical signal measurements or time-resolved Doppler yet.

## 2026-11-08 — IMPORTANT CORRECTION: HELIX FOR HELIX, TSI DEFERRED

The user explicitly corrected the preceding directive: **develop Helix for Helix itself now; do NOT develop for TSI. TSI work is postponed until access becomes available.** This entry supersedes the earlier "Helix for TSI" note in this checkpoint. Continue independent Helix signal intelligence research and testing. The corrected source of truth is https://github.com/jbackk-lang/Helix-Lock/blob/experiment/chiral-memory-retention/docs/TSI_HELIX_DEVELOPMENT_DIRECTIVE.md (correction commit `c175fc49ee336ad8d1e5b358ec6913a9e312d3c6`).

## 2026-11-08 18:07+ UTC — Helix-for-Helix prototype implementation

Implemented isolated `HelixChiralIntelligence` in Helix-Lock (`experiments/helix_chiral_intelligence.py`, `tests/test_helix_chiral_intelligence.py`, `docs/HELIX_CHIRAL_INTELLIGENCE.md`). Input: timestamped angular phases with optional phase calibration; output: winding sign or abstention, QPSK symbol only if calibrated, coherence/evidence scores, anomaly flag and bounded history. The algorithm fits common phase independently for each winding hypothesis; evidence is **not** a calibrated probability. Mirror echo can mislead the observed winding; no security action. CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42508481223 pending at checkpoint (workflow commit `dda6abe703f4a22bb213d56140e8f67bcef1fc5b`). Scope: **Helix for Helix**, TSI deferred.

## 2026-11-08 — Helix Native evidence-first track

User requests demonstrating the new native Helix approach with tests, including real files; user testing can contribute evidence but does not establish cryptographic security. Created `archive/legacy-crypto` snapshot and `experiment/helix-native` research branch. New files: `experiments/helix_native_codec.py`, `tests/test_helix_native_codec.py`, `docs/HELIX_NATIVE_EVIDENCE.md`. Codec maps bytes to synthetic angular QPSK phase samples, decodes using HelixChiralIntelligence, and checks unkeyed SHA-256 for accidental corruption. **It is NOT encryption, does NOT authenticate data, and must not protect confidential files.** Production defaults unchanged. Python 3.11/3.12 CI: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42508884635 (pending when written). The preceding chiral intelligence CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42508481223 completed successfully. Next: measure size/speed, corruption and noise sensitivity; devise and independently analyze a threat model before making any security claims.

## 2026-11-08 — Helix Native measurable benchmark

Added `experiments/helix_native_benchmark.py` and `tests/test_helix_native_benchmark.py`, deterministic seed-based benchmarks of 16/64/256-byte binary samples (three trials), size expansion, encode/decode time and exact roundtrip under Gaussian phase noise at 0/0.12/0.5 radians. A noise-corrupted record is counted successful only if it exactly reconstructs the original; exceptions are failures. CI publishes JSON artifacts for Python 3.11 and 3.12: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42509130840 (pending when written). The previous real-file codec CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42508884635 succeeded for both versions. No cryptographic-security claim.

## 2026-11-08 — compact symbol storage and matched history baseline

Previous benchmark CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42509130840 **passed** for Python 3.11 and 3.12. Added `experiments/helix_native_compact.py` and `tests/test_helix_native_compact.py`: symbolic 2-bit QPSK packing, 45-byte header, direct plaintext payload, SHA-256 accidental corruption check; no secrecy/authentication, no physical sample noise preservation. Added `experiments/helix_native_history_comparison.py` and matching tests: same synthetic observations, instantaneous estimate versus temporal majority of decided signs; measure accuracy, coverage and reversal delay (history may hurt during reversals). CI https://github.com/jbackk-lang/Helix-Lock/actions/runs/42509363287 pending when recorded. **Do not claim improved intelligence without benchmark evidence.**
