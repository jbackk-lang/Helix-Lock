# Helix Native: evidence-first research track

**Scope:** Helix for Helix. TSI is deferred.

## Repository separation
- `archive/legacy-crypto`: snapshot of prior experimental branch; preserved for reference, not deleted.
- `experiment/helix-native`: independent research and verification. No merge into `main` and no change to production encryption defaults.

## Real-file research experiment
`experiments/helix_native_codec.py` encodes each byte into four synthetic QPSK symbols, represented as angular phase samples. `HelixChiralIntelligence` decodes these with an explicit phase reference. A SHA-256 digest detects accidental mismatches after decoding.

**This is not encryption.** Encoded data is publicly reversible. An attacker can change the data and recompute its unkeyed digest. It provides **no confidentiality, authenticity, tamper resistance, or secure storage**. Never use it to protect private files. Tests with real files demonstrate only reversible representation and corruption detection under the test model.

## Evidence gates
1. Exact roundtrip of empty, binary and random real files; no partial output after failed decode.
2. Explicit negative tests for modified phase, missing records, ambiguous geometry and missing phase reference.
3. Noise, reflection, phase drift, file size and speed benchmarking versus simple raw/encoded baselines.
4. Formal threat model, cryptanalysis and independent review before any security claims.
5. Keep legacy authenticated encryption available for actual confidential files; no user testing can substitute for security evidence.

Run: `python -m pytest -q tests/test_helix_native_codec.py`.

## 2026-11-08 — key-management decision

The user decided that **Helix will use established solutions for keys**, rather than inventing its own key generation or key-management scheme. Recommended engineering boundaries:

- Use a cryptographically secure random number generator for fresh keys/nonces; established password-based KDFs (e.g. Argon2id where appropriate), and standard key storage/rotation mechanisms.
- Treat Helix-native chirality/phase/memory algorithms as a separately validated research layer, not as proof of confidentiality or authentication.
- Keep a reviewed authenticated-encryption primitive for actual confidential file protection until an independently validated alternative exists.
- Specify key derivation, domain separation, nonce uniqueness, metadata authentication, versioning, recovery and migration in a future implementation design; do not improvise cryptographic primitives.
- No user passwords or keys in experiment logs or public CI artifacts.

Decision scope: **Helix for Helix**, not TSI.
