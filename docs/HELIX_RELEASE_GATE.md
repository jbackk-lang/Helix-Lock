# Helix-Lock release decision: experiment/helix-native

Status: **FEATURE FROZEN; NOT READY TO MERGE** (security-first gate).

Verified CI: https://github.com/jbackk-lang/Helix-Lock/actions/runs/42515042169
(commit 229a273bf70480eff268c33963d6a475239714f7, successful).
This verifies automated tests, not production security or a release tag.

Release scope is frozen: HNA1 file envelope, experimental HNS1 streaming
file envelope, and existing decoding experiments. No new algorithm work.
Replay receiver is EXCLUDED from this release. Its experimental files remain
in the research branch but are not part of the supported release surface.
Do not include replay receiver code in packaging or enabled runtime paths.

## Decisions

1. **AES-256-GCM is the authenticated encryption boundary.** Phase coding,
   resonance filtering, coherence, and symbol consensus are not cryptography.
2. **Symbol consensus is an optional decoding heuristic.** It cannot defend
   against correlated echo. The regression in
   `tests/test_helix_release_blockers.py` demonstrates that seven unanimous
   observations can still be wrong when all share a phase-biased reflection.
   Do not promote the consensus path as an anti-echo security feature.
3. **Release boundary:** the replay receiver and its checkpoint/recovery
   subsystem are excluded from the supported release. They do not block
   file encryption/decryption release once their absence from runtime and
   packaging has been verified.
4. **CI success is necessary but insufficient.** Synthetic deterministic tests
   do not prove real-world echo handling, key lifecycle, file-write durability,
   or resistance to compromise of the checkpoint authority.

## Required before main merge

- [ ] Verify the replay receiver is absent from release entry points,
      package contents, and supported execution paths.
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
