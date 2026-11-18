# Omega cascades: measured synthetic comparison (2026-11-18)

Status: local Python reproduction of committed search algorithms, **not** GitHub CI and **not** full HLOM archive sizes.

Setup: six deterministic synthetic samples, 8192 bytes each, seed 42, zlib level 6. Common predictor uses 2-byte estimated selector overhead; independent uses 1+lanes bytes; cascade uses 2+stage count bytes, plus one byte per separate compressed branch. Baseline raw zlib has no selector overhead. Values below are bytes, lower is better.

| Sample | Raw zlib | Common multi-branch | Independent per branch | Cascade best |
|---|---:|---:|---:|---:|
| Random | 8203 | 8205 | 8205 | 8203 (baseline) |
| Gradient | 353 | 33 | 33 | 34 |
| Rows | 439 | 65 | 65 | **38** |
| RGB-like | 875 | 37 | 37 | 38 |
| Periodic | 35 | 37 | 37 | 35 (baseline) |
| Mixed three channels | 5450 | **52** | 53 | 53 |

On row-structured data, the winning cascade is SUB(lag=1) followed by SUB(lag=256), with one branch and joint zlib. It reduces the estimated compressed size from 65 to 38 bytes compared with the best earlier single/common predictor (41.5% smaller). The cascade does **not** improve the other five samples.

Caveats: This is a reproduction of the Python algorithms and their scoring, not a run of the checked-out repository's test suite. Header and selector costs are estimates, not a serialized format. No AES-GCM, GF(256) parity, metadata, memory, or decode-time measurements. No results on real files and no commercial-tool comparison. Synthetic test cases were used to develop the candidates; no held-out evidence of generalization.

Next: add a true reversible on-disk experimental codec with exact selector serialization, benchmark archive bytes, run tests in CI, then evaluate held-out real-world files before considering HLOM integration.
