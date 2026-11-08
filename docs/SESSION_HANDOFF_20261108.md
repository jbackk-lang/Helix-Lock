# Handoff: Helix-Lock / GIA-TIMDR / TSI

**Prepared:** 2026-11-08
**Purpose:** continuation note for the next ChatGPT session. Read this before continuing work.

## User's current priorities
- Continue Helix-Lock work while the user prepares a large TSI source archive.
- TSI's core is based on a helix. Treat the TSI audit as strategically important and keep a parallel research track, but do not modify TSI before inspecting its source.
- The user expects concrete repository work and documentation, not claims of background activity.
- Preserve original code and report uncertainty honestly.

## Repository scope
- Helix-Lock: https://github.com/jbackk-lang/Helix-Lock
- GIA-TIMDR: https://github.com/jbackk-lang/GIA-TIMDR
- TSI repository discussed: https://github.com/jbackk-lang/AI-SI-TSI
- TSI archive is local to the user's Windows machine at H:\\TSI. It was split into 20 large parts and later into many small logical ZIP packages. Parts TSI_01.zip through TSI_20.zip were uploaded in one batch, but they were not successfully materialized/read due per-file size limits. User decided to resume TSI transfer tomorrow around 17:00. Do not claim that the complete TSI archive has been received or audited.

## Helix work already recorded
- AIRPMonitor in-memory event buffer bounded; exposes dropped_events. This is a recent-events buffer, not durable audit storage.
- AIRPHistoryMemory prototype: fixed-window metadata summaries, bounded working state O(window_size), strict sequence continuity and timezone-aware timestamps, summary hash and source-checkpoint reference. It does not itself verify a signed checkpoint and is not an audit source of truth.
- Synthetic three-loop phase-memory model and tests. Previous reported result: mean phase error 1.27539 rad (no coupling/no memory), 0.72049 rad (coupling only), 0.58147 rad (coupling plus explicitly added reference-feedback law), 100 seeds. This is only a toy-model result; not evidence of self-repair in production Helix, GIA-TIMDR, or TSI.
- Negative synthetic TIMDR benchmark result documented: candidate feature had worse false-positive rate than simple baseline. Do not hide or tune against holdout.
- Chronoprocess boundary note documents that current GIA-TIMDR Chronoprocess is an orchestrator of three projections (M/S, G, K), not itself adaptive history memory or coupled phase self-repair.
- Recent experiment change adds selectable disturbance targets (one, two, or all three loops) and a common-mode control test. Common-mode disturbance moves all phases together and preserves relative phase; it is not repair.
- Workflow pull_request path filter was missing the phase-memory experiment and test paths; fixed in commit ca9a8eda055b975aceff31925ae72d13fcb6c146.

## Recent commits (Helix-Lock main)
- ca9a8ed — CI: include phase-memory experiment paths in pull requests.
- a4568b2 — experiment: parameterize disturbances across all three loops.
- 358e2e0 — tests: common-mode three-loop disturbance control.
- cdffc85 — docs: record common-mode control and CI path correction.

## Immediate next tasks
1. Check GitHub Actions for the latest commit. Do not state PASS until both Python 3.11 and 3.12 jobs have completed successfully. If failed, inspect job logs and fix the actual defect.
2. Run/extend the three-loop experiment with pre-registered cases: disturbance on loop 1, 2, or 3 separately; equal common-mode disturbance on all three loops; disturbances on all three loops with unequal amplitudes; sweep duration and amplitude; include frequency heterogeneity and bounded noise; compare no coupling, coupling only, coupling plus reference feedback.
3. Add a stale-reference / legitimate-state-transition test. Demonstrate whether feedback to an old stored reference can resist a valid new state. Treat this as a potential failure mode; do not present reference memory as universally beneficial.
4. Report more than one aggregate mean: median, spread/quantiles, fraction reaching a defined recovery threshold, recovery time, overshoot, and failure-to-recover rate. Define metrics before parameter tuning. Separate calibration and holdout seeds.
5. Keep phase coherence, reference recovery, payload integrity, and payload reconstruction as separate metrics. Do not equate them.
6. Do not connect AIRPHistoryMemory to authorization or key rotation without a separate threat model, independent checkpoint verification, and explicit tests.
7. Keep README and research notes current; cross-reference relevant results in AI-SI-TSI notes only as research context, not as claims about implemented TSI behavior.

## TSI transfer instructions for next session
- Ask whether user has resumed transfer; expected around 17:00 next day from 2026-11-08.
- User wants TSI only, excluding Math Validator and TSI-MUZ.
- Packaging difficulty: source archive ~2.35 GB; 90 MiB part limit and 20-attachment-per-message limit led to approximately 75 logical packages. User preferred pausing rather than continuing immediately.
- If user uploads parts, track exact numbering and count. Never claim completeness until all expected parts are accounted for.
- Inspect each attachment's actual size/accessibility. Previous files larger than 100 MiB could not be materialized in the analysis environment. Ensure each package is comfortably below 100 MiB (e.g. 80–90 MiB).
- If there are more than 20 packages, receive them in multiple messages. After all parts arrive, concatenate only if they are raw split chunks; if they are logical ZIP packages, extract each into a staging directory while preserving relative paths. Detect collisions and duplicate paths; do not silently overwrite.
- Verify each ZIP integrity and produce a file manifest with path, size, and SHA-256. Compare against a manifest created on the user's machine if available.
- Audit source read-only first: architecture map, helix implementation, triple-loop transitions, Chronoprocess/time, memory/compression, data continuity, tests. Do not change source code or publish it without explicit permission.
- Never infer behavior from filenames or README alone; trace call sites and tests.

## Communication rules
- Be transparent about what was actually fetched, changed, tested, and committed.
- Distinguish source-code facts, toy-model results, and hypotheses.
- Do not promise ongoing background work between turns.
- Continue in Polish unless user changes language.

## Additional work after initial handoff (2026-11-08)

- `a4270f6`: exposed `reference_feedback_correction()` for direct analysis of the stale-reference effect; fixed `run()` so generator/iterator seeds are materialized once and reused across all modes; records actual seed values.
- `b1eecde`: tests that a stale reference produces a correction opposing a legitimate phase shift, and that generator seeds are applied consistently to all modes.
- `9e247b6`: documents the stale-reference hazard and iterator regression.
- Earlier in the same continuation: `ca9a8ed` fixed pull_request path filters; `a4568b2` added disturbance target selection; `358e2e0` added common-mode control tests; `cdffc85` documented them.
- IMPORTANT: check Actions after the latest commits. The previously observed successful run was for commit `358e2e0`, before the newer stale-reference commits. Do not claim the newest code passed CI until its run completes.
- Next: run Actions, fix any failures, then implement a pre-registered amplitude/duration/frequency heterogeneity sweep with held-out seeds and report median/p90/max/recovery fraction/recovery time/overshoot. Also model legitimate state transition as a first-class case, not only the correction sign.


## Desktop v0.1.0 readiness work (2026-11-08, later session)

- `8c6ee9b`: fixed release workflow. It now publishes only on a version tag matching `v*`, uses `github.ref_name` rather than hard-coded `v0.1.0`, and manual dispatch/main/PR runs build artifacts without publishing a release.
- `bcbd1d5`: added cross-platform packaging validation for app/core changes on main and pull requests.
- `ad82487`: added `docs/RELEASE_CHECKLIST.md` with manual smoke tests, distribution trust and security limitations.
- `4ada1c1`: linked release checklist from README.
- `4965def`: recorded successful cross-platform build run.
- Build workflow run [42501965166](https://github.com/jbackk-lang/Helix-Lock/actions/runs/42501965166) completed successfully at commit `bcbd1d584e4e9d8c4ba1465571960c7c6f5716b0`. Windows, macOS and Linux PyInstaller/package/upload jobs all passed. Release job was correctly skipped because this was not a version tag.
- Artifacts: Windows 16,171,183 bytes; macOS 14,940,876 bytes; Linux 31,178,150 bytes. They are CI artifacts, not a published GitHub Release.
- Still required before calling v0.1.0 complete: inspect/download artifact contents, test each build on a real target OS, verify round-trip and tamper rejection, verify hashes, and arrange signing/notarization if desired. No independent security audit has been performed.
- Latest release checklist: `docs/RELEASE_CHECKLIST.md`. Do not create/push a release tag until manual checks are complete and the owner explicitly approves publishing.
