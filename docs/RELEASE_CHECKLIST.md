# Helix-Lock v0.1.0 — release checklist

## Purpose and release scope

v0.1.0 is a first desktop/application release candidate, not a claim of independent security certification. The production file-encryption path uses AES-256-GCM through `cryptography`; the AIRP, history-memory and phase experiments are prototypes and must not be described as validated intrusion detection or self-repair.

## Automated gates

- [ ] `Helix-Lock AIRP tests` passes on Python 3.11 and 3.12.
- [ ] `Build and publish Helix-Lock desktop release` passes on Windows, macOS and Linux.
- [ ] Build artifacts exist for all three platforms and contain the expected executable/app bundle.
- [ ] SHA-256 manifest is published with the release.
- [ ] Release is created only from an intentional `v*` tag. Manual workflow dispatch and ordinary main-branch pushes must build artifacts only, never publish a release.

## Manual smoke tests required before calling the desktop app ready

- [ ] Windows: launch app, encrypt/decrypt a text file, image, already-compressed file and empty file; compare SHA-256 of original and decrypted files.
- [ ] macOS: repeat the same tests on a real macOS machine.
- [ ] Linux: repeat the same tests on a real Linux desktop session.
- [ ] Verify key-file mode and password mode independently; test wrong key/password and modified ciphertext.
- [ ] Verify fingerprint and AIRP screens with no database, a valid local database, a tampered ledger, and absent/unavailable external trust anchor.
- [ ] Confirm UI labels and dialogs are readable at supported display scaling; test keyboard navigation and long paths.
- [ ] Confirm no plaintext, password or secret key is written to logs or the AIRP ledger.

## Distribution and trust

- Build artifacts are currently unsigned. Do not describe them as publisher-verified or SmartScreen/Gatekeeper trusted.
- Windows Defender or other endpoint protection may flag unsigned PyInstaller bundles heuristically. A warning is not proof of malware, but neither should it be bypassed casually. Preserve the detected file, hash and Defender report; investigate reproducibly. Do not tell users to disable protection or add broad exclusions.
- Publish SHA-256 hashes and build metadata. Users should compare the downloaded package hash before running it.
- Code signing/notarization for Windows and macOS is a separate release task and requires the owner's signing identities/certificates.

## Security limitations that must remain visible

- The application integration and file container format have not had an independent security audit.
- AES-GCM nonce uniqueness depends on correct random generation and key lifecycle; key backup and separate secure storage are the user's responsibility.
- Local SQLite hash chains alone do not prevent full database rollback. An independently administered trust anchor/quorum is needed for that property.
- CounterLock's embedded counter is not a global anti-replay service by itself. The relying application must compare against independently persisted monotonic state.
- AIRPHistoryMemory is an analytical summary, not an audit ledger, authorization source, plaintext recovery mechanism or proof of self-repair.
- Synthetic phase-memory experiments are explanatory toy models, not production behavior or evidence of cryptographic security.

## Release procedure

1. Complete automated gates and manual smoke tests.
2. Review the release notes and security limitations.
3. Create and push a version tag such as `v0.1.0` at the reviewed commit.
4. Confirm all three platform builds finish successfully.
5. Confirm the GitHub Release contains all platform archives, build metadata and `SHA256SUMS.txt`.
6. Download each archive and verify its SHA-256 independently before announcing the release.
7. If any gate fails, do not publish; fix the cause and create a new version tag.

## Current state

The release workflow has been corrected so it publishes only on a `v*` tag and uses the actual tag name. Main-branch and pull-request changes to the desktop app now trigger cross-platform package builds as validation. The first such run must complete before this checklist can be considered satisfied. Manual GUI smoke tests on real Windows/macOS/Linux machines remain outstanding.

## Automated build validation result (2026-11-08)

Workflow run [42501965166](https://github.com/jbackk-lang/Helix-Lock/actions/runs/42501965166) completed successfully for commit `bcbd1d584e4e9d8c4ba1465571960c7c6f5716b0`.

All three packaging jobs passed:
- Windows: PyInstaller build, ZIP packaging, build metadata upload.
- macOS: PyInstaller app bundle, ZIP packaging, build metadata upload.
- Linux: PyInstaller build, tar.gz packaging, build metadata upload.

Artifacts were produced (not yet a public GitHub Release):
- `HelixLock-windows` — 16,171,183 bytes.
- `HelixLock-macos` — 14,940,876 bytes.
- `HelixLock-linux` — 31,178,150 bytes.

The release job was correctly skipped because this was a main-branch validation run, not a version tag. This confirms packaging/build steps, not runtime behavior on real desktop systems. Manual GUI smoke tests, code signing/notarization, downloaded-package hash verification, and independent security audit remain outstanding. Do not call v0.1.0 released yet.


## Workflow trigger separation

Desktop package validation lives in `.github/workflows/desktop-build.yml` and runs on relevant main-branch changes, pull requests and manual dispatch. Publishing lives in `.github/workflows/publish-release.yml` and runs on `v*` tags (or can be manually dispatched for build-only validation); the release job itself is guarded by a `refs/tags/v` condition. This separation avoids ambiguous branch/tag path-filter combinations and prevents a manual build from creating a release.


## Separate desktop-build workflow result (2026-11-08)

After separating tag publishing from normal build validation, [desktop build run 42502363536](https://github.com/jbackk-lang/Helix-Lock/actions/runs/42502363536) completed successfully for commit `af8e6f2f48d39d472de85cb5d6c83dd14924c03f`. Windows, macOS and Ubuntu jobs each passed the PyInstaller build, platform packaging and artifact upload steps. This is the canonical build-validation workflow going forward. It does not replace manual runtime testing on each OS.
