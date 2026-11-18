"""Reproducible head-to-head Omega predictor benchmark.

Runs existing search implementations on the same bytes. Reports real zlib
payload sizes plus *estimated* selector overhead (not full HLOM bytes).
Use --size 8192 for quick checks or --size 32768 for fuller exploration.
"""
from __future__ import annotations

import argparse
import json
import random
import time

from experiments.omega_branch_search import search as common_search
from experiments.omega_branch_independent import search as independent_search
from experiments.omega_cascade_search import search as cascade_search


def samples(size: int, seed: int) -> dict[str, bytes]:
    if size < 0:
        raise ValueError("size must be nonnegative")
    rng = random.Random(seed)
    return {
        "random": rng.randbytes(size),
        "gradient": bytes(i % 256 for i in range(size)),
        "rows": bytes(((i // 256) * 3 + i % 256) % 256 for i in range(size)),
        "rgb": bytes((i // 3 + (0, 30, 60)[i % 3]) % 256 for i in range(size)),
        "periodic": (b"ABCD" * ((size + 3) // 4))[:size],
        "mixed_channels": bytes(
            (i // 3 + (0, 100, (i // 3) % 7)[i % 3]) % 256 for i in range(size)
        ),
    }


def compare(data: bytes) -> dict:
    strategies = (
        ("common", common_search, lambda r: r["best"]["estimated_bytes_with_selector"]),
        ("independent", independent_search,
         lambda r: r["best"]["estimated_bytes_with_selectors"]),
        ("cascade", cascade_search, lambda r: r["best"]["bytes"]),
    )
    results = {}
    baseline = None
    for name, run, extract in strategies:
        started = time.perf_counter()
        outcome = run(data)
        if name == "common":
            baseline = outcome["baseline_zlib_bytes"]
        results[name] = {
            "estimated_bytes": extract(outcome),
            "search_ms": round((time.perf_counter() - started) * 1000, 3),
            "best": outcome["best"],
        }
    winners = sorted(
        [("raw_zlib", baseline)] +
        [(name, result["estimated_bytes"]) for name, result in results.items()],
        key=lambda item: (item[1], item[0]),
    )
    return {"input_bytes": len(data), "baseline_zlib_bytes": baseline,
            "strategies": results, "winner": {"name": winners[0][0],
                                               "estimated_bytes": winners[0][1]},
            "all_strategies_beating_baseline": [
                name for name, result in results.items()
                if result["estimated_bytes"] < baseline
            ]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=8192)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    if args.size < 0:
        parser.error("--size must be >= 0")
    rows = [{"sample": name, **compare(data)}
            for name, data in samples(args.size, args.seed).items()]
    output = {"status": "experimental_synthetic_estimated_overhead",
              "sample_size": args.size, "seed": args.seed,
              "limitations": [
                  "No encryption, GF256 recovery, HLOM headers, or memory measurements",
                  "Selector sizes are estimates, not a serialized bitstream",
                  "Search time includes Python candidate enumeration and is not codec throughput",
                  "Synthetic patterns do not establish performance on real files",
              ], "results": rows}
    rendered = json.dumps(output, indent=2, sort_keys=True)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
