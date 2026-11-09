# HTKE 0.1 — Helical TIMDR Key Evolution

**Status:** research specification / branch bootstrap. Not production cryptography.  
**Branch:** `experiment/htke-helical-key-evolution`  
**Parent:** `main` at the branch point.  
**Scope:** derive and manage per-epoch AES-256-GCM data-encryption keys using an authenticated, versioned TIMDR state context. The AES-GCM primitive remains unchanged.

## 1. Purpose and non-goals

HTKE investigates whether the mathematical state represented by TIMDR can provide a useful, deterministic *context* for key epochs in HELIX-LOCK.

HTKE does **not**:
- replace AES-256-GCM, HKDF, a cryptographically secure random generator, or a key-management system;
- treat geometry, phase, timestamps, counters, hashes, or public state as secret entropy;
- claim that a helix or a changing phase is inherently cryptographically strong;
- rotate keys in response to noisy measurements or an unvalidated anomaly score;
- claim forward secrecy merely because a key changes between epochs.

The security contribution, if any, must come from correct key separation, authenticated state transitions, anti-rollback controls, safe key lifecycle and independently validated implementation—not from visual or geometric complexity.

## 2. Findings from the current TIMDR code

The existing `TIMDR-Time-Formalism/timdr_time/chronoprocess.py` is an orchestrator of three distinct projections of a shared carrier:
- M/S: tempo and drift of the supplied time series;
- G: a congruence surface built from time samples and a separate parameter domain;
- K: phase/interference evaluation for supplied modalities.

The branch specification explicitly preserves the non-identifiability of M/S, G and K. The current K implementation in `TIMDR-Modal-Formalism/timdr_modal/phase_sync.py` models constant `(f, phi, A)` modalities and affine phase synchronization. It is not a coupled, adaptive three-loop key scheduler.

The three-loop phase-memory experiments in HELIX-LOCK are synthetic dynamical toy models with an explicitly added feedback law. They are not the production Chronoprocess and do not establish cryptographic security or key-recovery properties.

**HTKE rule:** initially consume only explicitly selected, versioned outputs from TIMDR. Do not invent a single combined TIMDR vector or silently identify the M/S, G and K branches. Each projection has its own schema and provenance.

## 3. Threat model

Assets:
- root key material and derived epoch keys;
- encrypted payloads and their authenticated metadata;
- epoch ordering and object-to-key association;
- signed AIRP checkpoints and external anchor state.

Adversary capabilities to consider:
- modify, truncate, reorder, replay or replace encrypted objects and manifests;
- restore an older local database, file or process snapshot;
- supply malformed or extreme TIMDR observations;
- cause process crashes between key derivation, encryption, checkpoint publication and file replacement;
- obtain one current or historical epoch key;
- observe public manifests, state digests, salts, nonces and ciphertexts.

Out of initial scope: compromised host/kernel, memory scraping by a privileged attacker, malicious trusted anchor quorum, weak user passwords, and secure deletion guarantees on SSDs/backups. These require separate controls and claims.

## 4. Terminology

- **Root key:** high-entropy secret held by a key provider or protected key store. Never derived from TIMDR.
- **Epoch:** monotonic cryptographic generation for one object and one key purpose.
- **TIMDR state record:** canonical, versioned public context assembled from approved branch outputs.
- **HKSS:** Helical Key State Signature; in v0.1 this means a *public cryptographic digest/commitment* of the canonical state record, not a digital signature and not a secret.
- **Epoch manifest:** public metadata required to identify and validate the epoch and derive/open the corresponding key.
- **Anchor:** independently administered monotonic checkpoint service. A local SQLite ledger alone is not an anti-rollback anchor.

## 5. State record and canonicalization

A state record must be deterministic, schema-versioned and bounded. Candidate fields:
- schema identifier and schema version;
- TIMDR source repository/revision and adapter version;
- projection identifiers, separately namespaced (M/S, G, K);
- object identifier and key-purpose identifier;
- epoch number and previous accepted checkpoint reference;
- selected, documented state parameters and their units;
- quality/validity flags and source sequence/time range.

Rules:
1. Never serialize Python object representations, unordered mappings, NaN, Infinity, platform-dependent floats or locale-formatted numbers.
2. Define exact units, precision, normalization, null handling and field ordering.
3. Reject invalid, missing, stale or out-of-range state. Do not silently coerce it.
4. Preserve separate M/S, G and K namespaces; no arbitrary concatenation into an undocumented vector.
5. State is public context. Do not place keys, passwords, plaintext, raw secrets or unnecessary personal data in it.
6. A digest detects changes to the encoded record; it does not authenticate who produced it. Authentication comes from the trusted checkpoint/signature path.

Proposed identifier:
`HKSS = SHA-256("HELIX-HTKE-HKSS-v1" || canonical_state_record)`

The domain-separation label and encoding are part of the format. HKSS is not a key, entropy source, MAC or signature.

## 6. Reproducible epoch derivation (HTKE-R)

The first implementation candidate is a stateless, reproducible derivation from a high-entropy root key using HKDF-SHA-256.

Conceptually:
- IKM: root key supplied by a key provider;
- salt: independently generated public random salt recorded in the manifest (or a documented per-object salt policy);
- info: canonical, domain-separated context containing format version, object ID, key purpose, epoch, HKSS, and previous accepted checkpoint identifier;
- output: 32-byte AES-256 key.

Requirements:
- use a vetted HKDF implementation from the existing cryptographic dependency;
- enforce exact key and salt lengths and strict manifest validation;
- use distinct `info` labels for encryption, authentication/signing and any future subkeys;
- never use HKSS alone as IKM;
- never reuse an epoch identifier/context for a different plaintext generation;
- bind the serialized header/manifest bytes as AES-GCM AAD in a future format version;
- retain a tested migration path for existing HELIX formats.

A public salt and public HKSS do not add secrecy. Their role is key derivation context and domain separation. Security still depends on the secrecy and entropy of the root key.

## 7. Forward-evolution candidate (HTKE-F)

A separate experimental profile may use a one-way key ratchet, e.g. a domain-separated HMAC/HKDF step from the previous epoch key plus authenticated epoch context.

This profile must be specified separately from HTKE-R:
- erase prior in-memory key material where the platform/runtime permits, while documenting that Python cannot guarantee complete memory zeroization;
- define crash recovery and backup/recovery policy before enabling it;
- never silently derive an older key from a newer one;
- make the state transition and durable epoch record crash-consistent.

A one-way ratchet with deletion of old keys can protect past epochs against compromise of a later key, subject to implementation and deletion assumptions. It does **not** protect future epochs if the current ratchet key is compromised, because an attacker may calculate forward. Do not call this post-compromise security without an independently authenticated rekey mechanism.

## 8. Epoch transition protocol

A transition is not triggered by every phase fluctuation. It requires an explicit policy decision and a valid next state.

Abstract transition:
1. Read and verify the latest signed AIRP checkpoint and independent anchor.
2. Load the active object version, epoch and key identifier.
3. Validate the proposed TIMDR state record against schema, continuity and quality constraints.
4. Allocate exactly the next epoch; reject stale, duplicate, skipped or forked transitions unless an explicit recovery protocol authorizes them.
5. Derive the candidate epoch key.
6. Encrypt with a fresh CSPRNG nonce and AAD binding the canonical header/manifest.
7. Verify the produced ciphertext by decrypting it in-process and checking the expected plaintext digest where appropriate.
8. Stage the new representation and manifest.
9. Commit the AIRP registry transition and external checkpoint under a documented transaction/recovery protocol.
10. Atomically replace the active file representation; recover fail-closed after interruption.
11. Retire old key access according to the configured retention/recovery policy.

The current `AIRPFileTransaction` coordinates local file replacement with the AIRP registry, but the filesystem and SQLite cannot form one native OS transaction. External anchor publication and file commit ordering must be designed and tested as a protocol; do not assume the current transaction class automatically makes the whole distributed transition atomic.

## 9. Epoch manifest (draft schema)

Required logical fields:
- format magic and version;
- derivation profile (`HTKE-R` or future `HTKE-F`);
- KDF identifier and parameters;
- object ID and key-purpose ID;
- epoch number and key ID;
- salt;
- HKSS and state-record schema/version reference;
- previous checkpoint sequence/hash;
- nonce and ciphertext/tag representation reference;
- creation metadata with explicit UTC semantics.

The exact binary/canonical encoding is not yet frozen. The manifest must be authenticated as AAD. Avoid trusting unauthenticated header fields before tag verification except for bounded parser dispatch.

## 10. Failure and recovery policy

Fail closed on:
- missing or invalid root key;
- unknown schema, KDF, profile or algorithm identifier;
- invalid state record or failed continuity checks;
- rollback, replay or same-epoch fork;
- invalid checkpoint signature or anchor disagreement;
- missing staged file after a committed registry transition;
- GCM authentication failure.

Recovery must not invent a new epoch from incomplete state. It must either restore the latest independently anchored valid representation or require explicit administrative recovery with a new, audited epoch.

## 11. Security invariants

1. No plaintext is released before AES-GCM tag verification succeeds.
2. No key is derived from public TIMDR state alone.
3. Every object, epoch and key purpose has a distinct derivation context.
4. Every encryption uses a fresh nonce under its AES-GCM key; nonce uniqueness is mandatory.
5. Header and manifest fields that affect interpretation are authenticated as AAD.
6. An epoch is accepted only if it extends the latest independently anchored history.
7. A local hash chain is tamper-evident, not rollback-proof by itself.
8. TIMDR analytics cannot weaken cryptographic checks or authorize a transition on their own.
9. Old-key retention and deletion semantics are explicit and tested.
10. Existing HELIX-LOCK formats remain readable; HTKE is opt-in until reviewed.

## 12. Validation plan

Baseline comparisons:
- B0: current AES-256-GCM format;
- B1: AES-GCM with conventional random per-object/per-generation data keys and explicit key IDs;
- R1: AES-GCM with HTKE-R derivation context;
- F1: experimental HTKE-F ratchet, only after R1 is stable.

Required tests:
- deterministic derivation for identical root/salt/context;
- different outputs for changed object, epoch, purpose, state digest or salt;
- rejection of malformed and non-canonical state records;
- state serialization cross-platform vectors;
- manifest/header tampering rejected by AEAD;
- nonce uniqueness strategy and CSPRNG failure handling;
- replay, rollback, fork and missing-checkpoint cases;
- crash injection at every transition boundary;
- old-epoch recovery and key-retention policy;
- fuzzing/property tests for parser and canonicalizer;
- performance and memory measurements separated from security claims.

No security benefit is claimed merely because derived keys differ. HTKE must be compared against B1, not only against a weak or static-key baseline. Any claimed advantage must identify the threat it improves and the assumptions it adds.

## 13. Implementation stages

**Stage 0 — this document:** freeze terminology, scope and invariants.

**Stage 1 — pure state model:** implement canonical state records and HKSS digest only; no key derivation and no encryption changes.

**Stage 2 — derivation prototype:** implement isolated HKDF-R function with test vectors; do not integrate with GUI or default encryption path.

**Stage 3 — manifest and AAD:** define versioned format and authenticate all interpretation-critical metadata.

**Stage 4 — epoch registry:** integrate with AIRP and independently anchored monotonic checkpoints; add crash/fork/replay tests.

**Stage 5 — evaluation:** compare B0/B1/R1 and publish negative as well as positive results.

**Stage 6 — optional ratchet:** design and review HTKE-F separately.

## 14. Acceptance criteria for 0.1

- The state model is deterministic and versioned.
- M/S, G and K remain separately typed and traceable.
- Public state cannot substitute for secret key material.
- The HKDF derivation is domain-separated and has reproducible test vectors.
- The manifest is authenticated as AAD.
- Rollback and crash tests demonstrate fail-closed behavior against the stated local/anchor threat model.
- No production default changes until independent review and migration tests pass.

**Current status:** specification only. No cryptographic code has been added by this document. No claim of increased cryptographic strength is made.
