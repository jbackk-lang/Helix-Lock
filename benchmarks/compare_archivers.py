"""Reproducible archive benchmark: Helix-Omega vs optional 7z / RAR.

External archives are COMPRESSED WITHOUT ENCRYPTION. This measures size and
runtime only, NOT equivalent security, parity or resilience.
Usage: python -m benchmarks.compare_archivers path/to/file [path/to/other]
       python -m benchmarks.compare_archivers --synthetic
Outputs JSON lines. Never claims benchmark results without running.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from helix_pro.cipher import generate_key
from helix_pro.timdr_archive_cipher import encrypt_file_omega, decrypt_file_omega


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, cwd):
    start = time.perf_counter()
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.PIPE, timeout=300)
    return round((time.perf_counter() - start) * 1000, 3)


def measure(source, kind):
    source = Path(source).resolve()
    with tempfile.TemporaryDirectory(prefix="helix-bench-") as tmp:
        tmp = Path(tmp)
        original = tmp / "payload.bin"
        shutil.copyfile(source, original)
        size = original.stat().st_size
        expected = digest(original)
        if kind == "helix-omega":
            archive = tmp / "result.hlom"
            restored = tmp / "restored.bin"
            key = generate_key()
            t0 = time.perf_counter()
            encrypt_file_omega(original, archive, key=key)
            enc_ms = round((time.perf_counter() - t0) * 1000, 3)
            t0 = time.perf_counter()
            repaired = decrypt_file_omega(archive, restored, key=key)
            dec_ms = round((time.perf_counter() - t0) * 1000, 3)
            command = "HLOM (AES-GCM + HTO2/3/4)"
            encrypted = True
        elif kind == "7z":
            archive = tmp / "result.7z"
            restored = tmp / "out" / "payload.bin"
            (tmp / "out").mkdir()
            enc_ms = run(["7z", "a", "-t7z", "-mx=5", str(archive), "payload.bin"], tmp)
            dec_ms = run(["7z", "x", "-y", "-o" + str(tmp / "out"), str(archive)], tmp)
            repaired = None
            command = "7z compression only (NO encryption)"
            encrypted = False
        elif kind == "rar":
            archive = tmp / "result.rar"
            restored = tmp / "out" / "payload.bin"
            (tmp / "out").mkdir()
            enc_ms = run(["rar", "a", "-m3", str(archive), "payload.bin"], tmp)
            # unrar is commonly shipped with RAR, but may be unavailable
            extractor = "unrar" if shutil.which("unrar") else "rar"
            dec_ms = run([extractor, "x", "-o+", str(archive), str(tmp / "out") + os.sep], tmp)
            repaired = None
            command = "RAR compression only (NO encryption / recovery record)"
            encrypted = False
        else:
            raise ValueError(kind)
        return {
            "file": source.name, "input_bytes": size, "format": kind,
            "configuration": command, "encrypted": encrypted,
            "archive_bytes": archive.stat().st_size,
            "ratio": round(archive.stat().st_size / size, 5) if size else None,
            "encode_ms": enc_ms, "decode_ms": dec_ms,
            "sha256_verified": restored.exists() and digest(restored) == expected,
            "repaired_blocks": repaired,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args()
    if not args.files and not args.synthetic:
        parser.error("supply files or --synthetic")
    with tempfile.TemporaryDirectory(prefix="helix-samples-") as sample_dir:
        sources = list(args.files)
        if args.synthetic:
            for name, data in (
                ("zeros.bin", bytes(256 * 1024)),
                ("periodic.bin", b"ABCD" * (256 * 1024 // 4)),
                ("random.bin", os.urandom(256 * 1024)),
            ):
                p = Path(sample_dir) / name
                p.write_bytes(data)
                sources.append(p)
        formats = ["helix-omega"]
        if shutil.which("7z"):
            formats.append("7z")
        if shutil.which("rar") and (shutil.which("unrar") or shutil.which("rar")):
            formats.append("rar")
        for source in sources:
            for fmt in formats:
                try:
                    result = measure(source, fmt)
                except (OSError, subprocess.SubprocessError, ValueError) as exc:
                    result = {"file": source.name, "format": fmt, "error": str(exc)}
                print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
