"""Benchmark experimental OBX1 against zlib on actual local files.

Usage: python -m benchmarks.omega_block_files path/to/file [other/file ...]
Never uploads or modifies input files. Reads each file fully into memory.
Not an encrypted-archive comparison: OBX1 has no AES-GCM or parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter
import zlib

from experiments.omega_block_codec import pack, unpack


def measure(path: Path, block_size: int = 32768) -> dict:
    data = path.read_bytes()
    start = perf_counter()
    baseline = zlib.compress(data, 6)
    zlib_encode_ms = (perf_counter() - start) * 1000
    start = perf_counter()
    assert zlib.decompress(baseline) == data
    zlib_decode_ms = (perf_counter() - start) * 1000
    start = perf_counter()
    encoded = pack(data, block_size=block_size)
    obx_encode_ms = (perf_counter() - start) * 1000
    start = perf_counter()
    restored = unpack(encoded)
    obx_decode_ms = (perf_counter() - start) * 1000
    if restored != data:
        raise RuntimeError("OBX1 roundtrip mismatch")
    return {
        "filename": path.name, "sha256": hashlib.sha256(data).hexdigest(),
        "input_bytes": len(data), "zlib_bytes": len(baseline),
        "obx1_bytes": len(encoded), "obx1_minus_zlib_bytes": len(encoded) - len(baseline),
        "zlib_encode_ms": round(zlib_encode_ms, 3),
        "zlib_decode_ms": round(zlib_decode_ms, 3),
        "obx1_encode_ms": round(obx_encode_ms, 3),
        "obx1_decode_ms": round(obx_decode_ms, 3),
        "roundtrip_ok": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--block-size", type=int, default=32768)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.block_size <= (1 << 20):
        parser.error("--block-size must be in [1, 1048576]")
    rows = [measure(path, args.block_size) for path in args.files]
    report = {
        "format": "OBX1 experimental unencrypted", "block_size": args.block_size,
        "limitations": [
            "No AES-GCM, HLOM framing or parity; not a secure archive comparison",
            "Single un-warmed timing; repeat measurements before performance claims",
            "Files are read in full; avoid sensitive input if sharing report hashes/names",
        ], "results": rows,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
