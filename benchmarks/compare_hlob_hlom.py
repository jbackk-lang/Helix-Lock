"""Reproducible encrypted-file comparison: HLOB vs HLOM.

Both modes use the same random AES-256 key and identical input. HLOM includes
GF(256) recovery; HLOB does not. Therefore size/speed are NOT feature-equivalent.
No user data is uploaded; temporary ciphertext is removed after each run.

Usage: python -m benchmarks.compare_hlob_hlom path/to/file --repeats 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import tempfile
from time import perf_counter

from helix_pro.timdr_archive_cipher import encrypt_file_omega, decrypt_file_omega
from helix_pro.timdr_obx_cipher import encrypt_file_obx, decrypt_file_obx

FORMATS = (
    ("HLOB", encrypt_file_obx, decrypt_file_obx),
    ("HLOM", encrypt_file_omega, decrypt_file_omega),
)


def measure(path: Path, repeats: int = 3) -> dict:
    if repeats < 1:
        raise ValueError("repeats must be positive")
    original = path.read_bytes()
    expected = hashlib.sha256(original).hexdigest()
    key = os.urandom(32)
    results = {}
    with tempfile.TemporaryDirectory(prefix="helix-comparison-") as temp:
        directory = Path(temp)
        source = directory / "input.bin"
        source.write_bytes(original)
        for label, encrypt, decrypt in FORMATS:
            enc_times, dec_times, sizes, repaired_counts = [], [], [], []
            for run in range(repeats):
                ciphertext = directory / f"{label}-{run}.archive"
                restored = directory / f"{label}-{run}.restored"
                start = perf_counter()
                encrypt(str(source), str(ciphertext), key=key)
                enc_times.append((perf_counter() - start) * 1000)
                sizes.append(ciphertext.stat().st_size)
                start = perf_counter()
                repaired = decrypt(str(ciphertext), str(restored), key=key)
                dec_times.append((perf_counter() - start) * 1000)
                if hashlib.sha256(restored.read_bytes()).hexdigest() != expected:
                    raise RuntimeError(f"{label} SHA-256 roundtrip mismatch")
                if label == "HLOM":
                    repaired_counts.append(repaired)
            results[label] = {
                "encrypted_bytes_median": statistics.median(sizes),
                "encrypted_bytes_min": min(sizes),
                "encrypted_bytes_max": max(sizes),
                "encrypt_ms_median": round(statistics.median(enc_times), 3),
                "decrypt_ms_median": round(statistics.median(dec_times), 3),
                "encrypt_ms_samples": [round(t, 3) for t in enc_times],
                "decrypt_ms_samples": [round(t, 3) for t in dec_times],
                "sha256_roundtrip_ok": True,
                "repaired_blocks": repaired_counts if label == "HLOM" else None,
            }
    return {
        "file": path.name, "input_bytes": len(original),
        "input_sha256": expected, "repeats": repeats,
        "formats": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    report = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "limitations": [
            "HLOM includes GF(256) parity; HLOB does not: functionality differs",
            "Both use AES-256-GCM, but format and metadata overhead differ",
            "No warmup, memory profiling, corruption injection or streaming",
            "Only local files; do not publish sensitive filenames or hashes",
        ],
        "results": [measure(path, args.repeats) for path in args.files],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
