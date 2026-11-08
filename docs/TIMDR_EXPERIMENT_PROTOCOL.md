# TIMDR M/S vs AIRP baselines — experiment protocol

**Status:** preregistration draft. No performance result is claimed by this document.

## Question
Does the read-only TIMDR M/S projection add measurable detection value over existing AIRP integrity checks and simple event-count/rate baselines on labelled event traces?

## Systems compared
A. **AIRP integrity baseline:** hash-chain verification, signed checkpoint verification, and the existing CounterLock monotonic-counter rejection. These are deterministic integrity/replay controls, not statistical anomaly detectors.

B. **Simple telemetry baseline:** fixed-window event count and denied-access count, with thresholds selected only on a calibration set.

C. **TIMDR M/S candidate:** fixed-window inter-arrival mean, inter-arrival drift, and event-rate deviation from a calibration baseline. The current adapter's in-sample mean-plus-two-standard-deviation flag is exploratory only and must not be treated as a validated detector.

## Data and labels
1. Generate synthetic benign traces representing steady use, bursty legitimate file operations, restart/recovery, synchronized access, and legitimate key rotation.
2. Generate synthetic labelled anomalies separately: replayed/decreasing counters, abrupt denied-access bursts, and unexpected rotation bursts. These are test scenarios, not claims about real attacks.
3. Preserve a final holdout generated from fixed seeds and not used to tune thresholds.
4. If real logs are later used, remove plaintext, keys, ciphertext, file paths, usernames, and stable object identifiers before analysis. Keep only event type, UTC timestamp, monotonic sequence, and coarse outcome labels.

## Metrics
- Event-level and window-level precision, recall, F1.
- False-positive rate on benign traces, reported separately by benign scenario.
- Detection delay from first labelled anomalous event.
- Runtime and memory overhead.
- For integrity/replay controls, report exact deterministic rejection separately; do not combine it into statistical detector accuracy.

## Controls and fairness
- Freeze feature definitions, window size, calibration procedure, thresholds, random seeds, and metrics before opening holdout.
- Give A/B/C the same input events and equivalent calibration access.
- Include ablations: rate only, denied count only, drift only, and combined TIMDR features.
- Report confidence intervals and raw confusion matrices; do not tune after seeing holdout.
- If the TIMDR candidate does not beat the simple telemetry baseline at an acceptable false-positive rate, report no demonstrated incremental value.

## Safety boundary
The adapter is read-only telemetry. It must not change ciphertext, keys, access decisions, counters, rotation, or recovery. Any future response policy remains separate and requires independent security review.

## Known implementation gap
The AIRP ledger currently emits event names including `registered`, `rotated`, `access` (with `payload.outcome`), and `counter_observed`. The adapter maps `registered`, `rotated`, `access` with explicit `granted`/`denied` outcomes, and `counter_observed`. The integration test should use these exact ledger event shapes. Unknown event names/outcomes must not be assigned inferred security meaning.

## Commercial-tool comparison (planned after the experiment)
The final report will compare Helix-Lock/TIMDR only against products in clearly matched categories: endpoint protection/EDR (for host behavior alerts), file/data encryption tools (for confidentiality and key lifecycle), and audit/immutable-log platforms (for tamper evidence and external anchoring). These are not interchangeable product classes. The comparison will use public vendor documentation and independently verifiable product capabilities, distinguish feature presence from measured performance, record product/version/date/licensing assumptions, and avoid claims that synthetic Helix-Lock results establish superiority over commercial products. Candidate products will be selected and researched when the internal experiment is complete.


## Executable synthetic benchmark harness

The first reproducible harness is `experiments/timdr_benchmark.py`. It uses fixed, disjoint calibration seeds (1000–1099) and holdout seeds (9000–9099), with 6,400 labelled windows. CI runs the harness and archives `timdr-benchmark.json` for 30 days. A reproducibility test checks that repeated runs return identical metrics.

Interpretation limits: this initial harness compares a simple rate/denied-count rule with the same rule plus an inter-arrival drift feature. It is deliberately a narrow ablation, not a complete implementation of the AIRP cryptographic-integrity baseline, not a validation on production traces, and not evidence of real-world attack detection. Synthetic scenario labels are not ground truth about adversaries. Results must be reported as exploratory.
