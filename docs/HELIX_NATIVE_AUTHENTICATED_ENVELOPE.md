# Helix Native authenticated file envelope (research integration)

The compact Helix symbol format remains experimental and publicly reversible. This module wraps it with **standard AES-256-GCM authenticated encryption**, using the maintained `cryptography` package. The authenticated envelope format is `HNA1 || 12-byte random nonce || AESGCM(ciphertext+tag)`, with fixed domain-separated associated data.

- The **security boundary is AES-256-GCM**, not chirality or the Helix phase transform.
- The key is a freshly generated 32-byte secret, managed separately from the file. The module does not implement password handling or key storage; do not put keys in Git, command-line arguments, logs, or CI artifacts.
- A wrong key, modified nonce, or modified ciphertext fails authentication. The output file is not created until authentication and decoding succeed.
- Nonces are randomly generated per encryption; a future production implementation must explicitly manage uniqueness, key rotation and limits.
- File I/O currently reads the entire file into RAM and is intended only for bounded experiments. It is **not** a production streaming implementation; large files, atomic destination writes, symlink protections, filesystem metadata and crash recovery require separate work.
- No merge to `main` or production replacement. This is an optional safety envelope around the original experimental format.

Run: `python -m pytest -q tests/test_helix_native_secure_envelope.py`.
