# Instructions for local-file-capable coding agent — Helix-Lock

> Handoff prepared 2026-11-18. This is a task brief, **not evidence that any local tests or benchmarks have run**.
> Repository: `jbackk-lang/Helix-Lock`. Work on an isolated branch, inspect current HEAD and existing instructions before editing. Do not overwrite unrelated changes.

## Objective

Validate and finish the **opt-in Helix-Omega file workflow** and produce an honest comparison with 7-Zip and RAR using actual local binaries and files. The user explicitly wants implementation, reproducible tests, measurable outcomes and commits, not unverified claims.

## Current implementation on main (verify against current HEAD)

- `helix_pro/cipher.py`: existing AES-256-GCM file encryption, HLXP and HLXN. **Do not break compatibility**.
- `helix_pro/timdr_archive_hto2.py`: compressed encrypted blocks with two GF(256) parity blocks per group.
- `helix_pro/timdr_archive_hto3.py`: redundant authenticated archive header.
- `helix_pro/timdr_archive_hto4.py`: reversible experimental RAW/1D/2D/3D predictors wrapping HTO3; **not a validated independent cipher or proven TIMDR triple-loop codec**.
- `helix_pro/timdr_archive_fast.py`: sampled 8 KiB predictor selection.
- `helix_pro/timdr_archive_cipher.py`: opt-in `HLOM` file API `encrypt_file_omega` / `decrypt_file_omega`, key or password. The AES-GCM layer still provides confidentiality.
- `tests/test_timdr_archive_cipher.py`: integration tests, and `.github/workflows/timdr-archive.yml`: CI matrix 3.11/3.12/3.13.
- `benchmarks/compare_archivers.py`: initial comparison runner; **7z/RAR currently run without encryption**, so its size/time results are not security-equivalent. No benchmark measurements have been verified by this handoff.

Recent integration commits: `934e2ac3` (file API), `ec700fc1` (tests), `d18bd5da` (CI), `0ccef788` (benchmark).

## Execution plan — local machine

1. Inspect repository state (`git status`, `git log -5 --oneline`, branches, Python environment) and existing docs, GUI entry points, tests and package dependencies. Work on a dedicated branch. Never commit generated test data, plaintext, keys, passwords or personal files.
2. Run `python -m pytest -q tests/test_timdr_archive_hto2.py tests/test_timdr_archive_hto3.py tests/test_timdr_archive_hto4.py tests/test_timdr_archive_fast.py tests/test_timdr_archive_cipher.py`. Record Python version, OS, commit SHA, duration, pass/fail and tracebacks. Repair actual failures with focused regression tests.
3. Audit HLOM for malformed/truncated input, wrong key/password, header tampering, output overwrite, resource exhaustion, oversized decompression and failed writes. Ensure authentication and decoding complete before replacing a target file; consider atomic output writes. Explicitly verify backward compatibility with HLXP/HLXN. Do not claim an external security audit.
4. Find the **actual GUI entry point** and integrate a clearly labeled optional `Helix-Ω (experimental)` mode with encrypt/decrypt, key/password handling and safe output naming. Preserve existing default AES workflow. Only make this change after confirming GUI architecture and adding tests. Do not silently change default format.
5. Execute `python -m benchmarks.compare_archivers --synthetic` and `python -m benchmarks.compare_archivers <local-test-file-1> <local-test-file-2>`. Use non-sensitive, redistributable or locally generated files. Detect and record versions/availability of `7z`, `rar`, `unrar`. If absent, report **not tested**, do not fabricate results. Check `benchmarks` import behavior and invocation from repo root; fix if necessary.
6. Improve benchmarking fairness: separate (a) compression-only and (b) encrypted archive comparisons, and (c) corruption/recovery tests. Record exact commands and settings (e.g. 7z `-mhe` when appropriate, RAR recovery record when appropriate). RAR can support recovery records: **never claim Helix alone has recovery**. Benchmark repeated runs (warmup, median, spread), report size, encode/decode time, throughput, memory when measurable, SHA-256 roundtrip verification. Do not compare HLOM encrypted bytes directly to unencrypted 7z/RAR as if security were equal.
7. For corruption tests, use disposable copies only; distinguish damaged data ciphertext, parity, authenticated metadata and selector header. Test 1/2/3 damaged data blocks and document what is and is not recoverable. Do not imply protection against arbitrary corruption.
8. Commit each coherent tested change with descriptive messages; push only to the intended branch and report PR/commit URLs. Do not publish releases, change tags or market this as production-ready without explicit user approval.

## Deliverables

- `docs/HELIX_OMEGA_INTEGRATION_STATUS.md`: actual architecture, entry points, compatibility and known limitations.
- `benchmarks/results/`: dated JSON/CSV and a short Markdown report with machine/OS, CPU, Python, external tool versions, exact settings, source file sizes and checksums, sample counts and measurement caveats. Do not include original user files.
- New/updated regression tests, and optional GUI integration only if validated.
- A concise Polish summary: **what changed, what passed, what failed, measured numbers, and what remains unproven**.

## Scientific and security boundaries

AES-256-GCM is the cryptographic engine; Omega predictors are preprocessing, not independently secure encryption. HTO2 parity has bounded repair capability. The HTO4 selector and other headers can be single points of failure. Compression gain and speed advantages are hypotheses until benchmarked. Avoid statements such as “better than AES”, “unbreakable”, “beats WinRAR” or “production secure”. Keep legacy formats readable and never destroy the only copy of user data.
