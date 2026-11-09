# Helix-Lock release gate — closed beta preparation

Status: **BETA PREPARATION — NOT READY FOR EXTERNAL TESTING OR STABLE RELEASE**.

The current branch is a development branch. The README must keep the visible
BETA TEST warning. No external beta recruitment or distribution has started.

## Supported scope for the first closed beta

Include only the existing desktop file workflow using the reviewed
AES-256-GCM implementation and the documented HLXP/HLXN formats, after
the release checks below are satisfied.

Explicitly exclude from the supported beta surface:
- HNS1 streaming envelope until its format, compatibility and independent
  security review are complete;
- Replay Receiver and checkpoint/recovery experiments;
- phase, resonance, coherence, symbol-consensus and history-memory research
  prototypes as security features;
- any module not reachable from the reviewed desktop workflow.

Do not silently enable experimental paths through packaging or GUI defaults.

## Security and product decisions

1. **AES-256-GCM is the authenticated encryption boundary.** Phase coding,
   resonance filtering, coherence, and symbol consensus are not cryptography.
2. AIRP local hash chains can detect local inconsistency but do not, by
   themselves, prevent rollback of the entire local database.
3. CounterLock's embedded counter is not a global anti-replay service by
   itself. The relying application needs independently persisted monotonic
   state.
4. Atomic file replacement protects against partial publication during
   ordinary write failures; power-loss durability and hostile filesystem
   races remain unverified.
5. CI success and beta feedback are necessary evidence, not proof of security.
6. Beta testers must use disposable copies and independent backups. No
   telemetry or automatic log upload is enabled by this plan.

## Required before closed beta

- [ ] Confirm the packaged app exposes only the supported HLXP/HLXN desktop
      workflow; verify HNS1, Replay Receiver and research prototypes are not
      enabled or represented as production capabilities.
- [ ] Review dependency inventory and build inputs; pin or otherwise record
      exact build dependency versions for reproducibility.
- [ ] Verify key creation, key storage guidance, password derivation,
      nonce generation and failure handling in the supported code path.
- [ ] Verify atomic file output and source/output alias protections, including
      failure-injection and practical filesystem tests.
- [ ] Review format compatibility and document any migration limitations.
- [ ] Confirm logs and error dialogs never expose passwords, key material,
      plaintext or file contents.
- [ ] Obtain green automated CI for the exact candidate commit.
- [ ] Owner completes practical smoke tests on available systems.
- [ ] Prepare platform artifacts, SHA-256 manifests and beta warnings.
- [ ] Enable a safe private vulnerability reporting route before inviting
      external testers.
- [ ] Recruit a small, diverse closed-beta group and provide the safety guide.

## Required before stable release

- [ ] No open P0/P1 beta findings.
- [ ] Reproducible bug reports have regression tests or documented rationale.
- [ ] Manual test coverage across supported Windows, macOS and Linux versions.
- [ ] Independent security review of the supported cryptographic integration
      and file formats.
- [ ] Signed/notarized builds where applicable, or clear unsigned-build
      warnings and verified SHA-256 manifests.
- [ ] Reviewed release notes, known issues, backup guidance and upgrade path.
- [ ] Owner explicitly approves the reviewed commit and version tag.

## Research work not in the release gate

Real/calibrated echo-channel measurements, decoding coverage thresholds,
phase memory, consensus and replay receiver research remain separate R&D.
They must not delay or be used to justify the security of the file-encryption
product. They also must not enter the supported release path without a
separate design review and explicit approval.

This file records the release decision and outstanding gates. It is not a
claim that the requirements have been met.
