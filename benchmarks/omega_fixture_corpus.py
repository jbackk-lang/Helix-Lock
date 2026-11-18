"""Generate a reproducible, non-sensitive Omega benchmark corpus.

Creates deterministic synthetic *file-like* workloads, not actual PDFs/PNGs.
No user files, passwords or cryptographic keys are included.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import zlib


def corpus(size: int = 32768, seed: int = 42) -> dict[str, bytes]:
    if size < 1:
        raise ValueError("size must be positive")
    rng = random.Random(seed)
    rows = bytes(((i // 256) * 3 + i % 256) % 256 for i in range(size))
    return {
        "random.bin": rng.randbytes(size),
        "gradient.bin": bytes(i % 256 for i in range(size)),
        "rows.bin": rows,
        "rgb-interleaved.bin": bytes(
            (i // 3 + (0, 30, 60)[i % 3]) % 256 for i in range(size)
        ),
        "mixed-channels.bin": bytes(
            (i // 3 + (0, 100, (i // 3) % 7)[i % 3]) % 256
            for i in range(size)
        ),
        "periodic.bin": (b"ABCD" * ((size + 3) // 4))[:size],
        "already-compressed.bin": zlib.compress(rows + rng.randbytes(size), 9),
        "mostly-zeros.bin": b"\x00" * (size - min(size, 128)) +
                            rng.randbytes(min(size, 128)),
    }


def write_corpus(destination: Path, size: int = 32768,
                 seed: int = 42) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {
        "kind": "synthetic Omega compression corpus",
        "size_parameter": size, "seed": seed,
        "files": [],
    }
    for filename, content in corpus(size, seed).items():
        path = destination / filename
        path.write_bytes(content)
        manifest["files"].append({
            "filename": filename,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("omega-ci-corpus"))
    parser.add_argument("--size", type=int, default=32768)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(write_corpus(args.directory, args.size, args.seed),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
