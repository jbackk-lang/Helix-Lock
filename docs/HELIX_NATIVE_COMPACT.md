# Helix Native compact phase-symbol representation

`experiments/helix_native_compact.py` stores four 2-bit QPSK indices per byte, with a common handedness flag and SHA-256 corruption check. It avoids materializing 12 floating-point sensor phases per symbol. Format: 4-byte magic, 1-byte sign, 8-byte big-endian length, 32-byte digest, then the **unchanged plaintext bytes**. Overhead is exactly 45 bytes.

**This is a compact symbolic encoding, NOT encryption, compression, authentication, or a substitute for the physical signal/channel model.** The payload is directly visible in the encoded bytes. A malicious party can replace it and recompute SHA-256. For real confidential files, continue using standard authenticated encryption separately.

The dense representation is suitable for storing the abstract symbols from which synthetic angular phases can later be generated. It does **not** preserve individual sensor noise, drift or reflection samples; those require the full experimental format.

The comparative tests verify exact roundtrip, shared handedness metadata, size reduction versus verbose JSON, and explicit confidentiality failure. A smaller representation does not imply greater security or greater information density than raw bytes.

Future work: benchmark history-aware vs memoryless inference on *matched observations* and record whether history helps; do not assume a benefit.
