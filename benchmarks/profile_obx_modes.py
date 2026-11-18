"""Profile OBX1 encoding modes without changing the OBX1 file format.

Run: python -m benchmarks.profile_obx_modes --size 1048576 --output obx-profile.json
This diagnostic measures encoding + zlib separately from AES-GCM; it does not
measure end-to-end HLOB encryption or make claims about other compressors.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
from time import perf_counter
import zlib

from benchmarks.omega_fixture_corpus import corpus
from experiments.omega_block_codec import MODES, _encode, pack, unpack


def profile(size: int = 1048576, repeats: int = 3, block_size: int = 32768) -> dict:
    if repeats < 1:
        raise ValueError("repeats must be positive")
    results = []
    for filename, data in corpus(size=size, seed=42).items():
        rows = []
        for mode in MODES:
            encode_ms, compress_ms, compressed_sizes = [], [], []
            for _ in range(repeats):
                start = perf_counter()
                encoded = b"".join(
                    _encode(data[i:i + block_size], mode)
                    for i in range(0, len(data), block_size)
                )
                encode_ms.append((perf_counter() - start) * 1000)
                start = perf_counter()
                compressed = [
                    zlib.compress(encoded[i:i + block_size], 6)
                    for i in range(0, len(encoded), block_size)
                ]
                compress_ms.append((perf_counter() - start) * 1000)
                compressed_sizes.append(sum(map(len, compressed)))
            rows.append({
                "mode": mode,
                "transform_ms_median": round(statistics.median(encode_ms), 3),
                "zlib_ms_median": round(statistics.median(compress_ms), 3),
                "compressed_payload_bytes_median": statistics.median(compressed_sizes),
            })
        archive = pack(data, block_size=block_size)
        if unpack(archive) != data:
            raise RuntimeError(f"OBX1 roundtrip failed: {filename}")
        results.append({
            "file": filename,
            "input_bytes": len(data),
            "obx_archive_bytes": len(archive),
            "roundtrip_ok": True,
            "modes": rows,
        })
    return {
        "size_parameter": size,
        "block_size": block_size,
        "repeats": repeats,
        "limitations": [
            "Synthetic data; not representative of arbitrary real files",
            "Encoding and compression measured separately; not end-to-end encryption",
            "Single-process timing; sensitive to runner load and Python version",
        ],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1048576)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = profile(size=args.size, repeats=args.repeats)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
