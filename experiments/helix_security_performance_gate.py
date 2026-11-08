"""Security regression and throughput gate for the existing AES-256-GCM envelope.

Threats tested: accidental/intentional byte modification, wrong key,
truncation and cross-message substitution. This is not a cryptographic proof.
Replay protection, key management and crash-safe writes are OUT OF SCOPE.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import time

from cryptography.exceptions import InvalidTag
from experiments.helix_native_secure_envelope import (
    generate_key, protect_bytes, recover_bytes, MAGIC, NONCE_BYTES,
)


def rejected(envelope: bytes, key: bytes) -> bool:
    try:
        recover_bytes(envelope, key)
    except (InvalidTag, ValueError):
        return True
    return False


def evaluate(*, sizes=(256, 4096, 65536), trials=5):
    rows = []
    for size in sizes:
        encrypt_times, decrypt_times, lengths = [], [], []
        checks = {"round_trip": 0, "tamper_rejected": 0,
                  "wrong_key_rejected": 0, "truncation_rejected": 0,
                  "header_rejected": 0, "unique_nonce": 0}
        nonces = set()
        for _ in range(trials):
            data = os.urandom(size)
            key = generate_key()
            start = time.perf_counter()
            envelope = protect_bytes(data, key)
            encrypt_times.append(time.perf_counter() - start)
            start = time.perf_counter()
            decoded, _ = recover_bytes(envelope, key)
            decrypt_times.append(time.perf_counter() - start)
            checks["round_trip"] += decoded == data
            lengths.append(len(envelope))
            nonce = envelope[len(MAGIC):len(MAGIC) + NONCE_BYTES]
            checks["unique_nonce"] += nonce not in nonces
            nonces.add(nonce)
            altered = bytearray(envelope)
            altered[-1] ^= 1
            checks["tamper_rejected"] += rejected(bytes(altered), key)
            checks["wrong_key_rejected"] += rejected(envelope, generate_key())
            checks["truncation_rejected"] += rejected(envelope[:-1], key)
            checks["header_rejected"] += rejected(b"BAD!" + envelope[len(MAGIC):], key)
        enc = statistics.median(encrypt_times)
        dec = statistics.median(decrypt_times)
        rows.append({
            "input_bytes": size, "trials": trials,
            "checks_passed": checks,
            "envelope_bytes": lengths[0],
            "overhead_bytes": lengths[0] - size,
            "encrypt_median_ms": enc * 1000,
            "decrypt_median_ms": dec * 1000,
            "encrypt_mib_per_s": size / (1024 * 1024) / enc,
            "decrypt_mib_per_s": size / (1024 * 1024) / dec,
        })
    return {"format": "helix-security-performance-gate-v1",
            "security_provider": "cryptography AES-256-GCM; Helix is not encryption",
            "limits": "Synthetic checks are not a security audit. Replay, nonce reuse across process restarts, "
                      "key lifecycle, malicious filesystem writes and large-file streaming not evaluated.",
            "results": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("helix-security-performance.json"))
    args = parser.parse_args()
    report = evaluate()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if any(any(value != row["trials"] for value in row["checks_passed"].values())
           for row in report["results"]):
        raise SystemExit("SECURITY REGRESSION: at least one check failed")


if __name__ == "__main__":
    main()
