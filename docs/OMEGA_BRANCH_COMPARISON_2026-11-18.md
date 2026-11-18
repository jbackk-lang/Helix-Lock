# Omega predictor strategies — local exploratory comparison (2026-11-18)

Status: **measured locally using a Python reproduction of the committed algorithms**, not a GitHub Actions run and not a full HLOM archive benchmark.

Each sample: 32,768 bytes; Python zlib level 6. Baseline is raw zlib. Single/common selector cost is estimated at 2 bytes; independent branch selector cost at 1 + number of branches. Encryption, parity, archive framing, execution time, and complete serialized selector metadata are excluded. Winner is selected using these estimated compressed sizes; ties resolved by iteration order. The independent strategy uses greedy per-branch selection, not a global optimum.

| Synthetic sample | Raw zlib | Single predictor | Common predictor, multi-branch | Independent per-branch | Best strategy |
|---|---:|---:|---:|---:|---|
| Random | 32784 | 32786 | 32786 | 32786 | Raw zlib |
| Gradient | 482 | 55 | 55 | 55 | Single SUB lag=1 (tie) |
| Row-structured | 717 | 167 | **127** (8 branches, SUB lag=1) | 141 (4 branches) | Common multi-branch |
| Interleaved RGB-like | 1044 | 60 | 60 | 60 | Single SUB lag=1 (tie) |
| Periodic | 58 | 60 | 60 | 60 | Raw zlib |
| Mixed three channels | 5688 | 113 | **85** (3 branches, SUB lag=1) | 86 (3 branches) | Common multi-branch |

## Findings

- Multi-branch preprocessing has genuine promise on structured synthetic data: row sample 717 -> 127 bytes and mixed-channel sample 5688 -> 85 bytes relative to raw zlib, under the stated selector assumptions.
- The **greedy independent per-branch method does not win any of these six samples**. In the mixed-channel sample it trails the common method by only one byte. Independent selection may need joint optimization, different branch distributions, or separate compressed streams to be worthwhile.
- The raw zlib baseline should always remain available, because selector overhead makes preprocessing worse on random and already compressible periodic data.
- These results do not demonstrate superiority over 7-Zip/RAR, on real files, or for the complete HLOM format.
- Next: test per-branch independent codecs and joint selector search on held-out real-world datasets; measure actual serialized archive bytes, decode time and memory. Do not change HLOM format until results are repeatable and reversibility is verified in the repository CI.

Reproduction: `experiments/omega_branch_search.py` and `experiments/omega_branch_independent.py` are in the repo. The above comparison was run using equivalent Python logic locally, because a GitHub checkout was not available in this environment.
