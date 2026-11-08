# Helix-Lock release decision: experiment/helix-native

Status: **FEATURE FROZEN; NOT READY TO MERGE** (security-first gate).

Verified CI: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42515042169
(commit 229a273bf70480eff268c33963d6a475239714f7, successful).
This verifies automated tests, not production security or a release tag.

Release scope is frozen: HNA1 file envelope, experimental HNS1 streaming
file envelope, and existing decoding experiments. No new algorithm work.
Do not enable replay-sensitive network receiving as a production feature
without an independent trusted checkpoint authority.

## Decisions

1. **AES-256-GCM is the authenticated encryption boundary.** Phase coding,
   resonance filtering, coherence, and symbol consensus are not cryptography.
2. **Symbol consensus is an optional decoding heuristic.** It cannot defend
   against correlated echo. The regression in
   `tests/test_helix_release_blockers.py` demonstrates that seven unanimous
   observations can still be wrong when all share a phase-biased reflection.
   Do not promote the consensus path as an anti-echo security feature.
3. **Replay state is not production-ready.** The SQLite guard can reject
   duplicates under tested concurrency, but persistent rollback resistance
   requires an external non-rollbackable checkpoint authority with a durable
   compare-and-swap operation. The current synchronized in-memory test double
   is not such an authority.
4. **Crash recovery is fail-closed, not automatic.** An external checkpoint
   advance followed by an uncommitted SQLite transaction can lock out the
   receiver. Recovery must independently establish whether the message was
   consumed. Never reset the checkpoint to match a rolled-back DB.
5. **CI success is necessary but insufficient.** Synthetic deterministic tests
   do not prove real-world echo handling, key lifecycle, file-write durability,
   or resistance to compromise of the checkpoint authority.

## Required before main merge

- [ ] Specify and implement a real trusted checkpoint backend, its threat
      model, crash recovery, key rotation, and durable CAS semantics.
- [ ] Add process-level crash injection and recovery tests against that backend.
- [ ] Validate echo/reflection behavior against independent real or calibrated
      channel traces; compare error rate AND abstention/coverage.
- [ ] Define release thresholds for accuracy, false acceptance, coverage,
      throughput, and regression on clean signals.
- [x] Verify atomic file output and injected ordinary write/replace failure
      behavior for HNA1 and HNS1 in CI. Power-loss durability and hostile
      filesystem races remain **unverified**.
- [ ] Review dependencies, format compatibility, and key handling.
- [x] Obtain green CI for current branch commit 229a273b (workflow run
      42515042169). Verify matrix coverage before asserting both versions.

This file records a decision, not a claim that these requirements are met.
