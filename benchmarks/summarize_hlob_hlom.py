"""Summarize real HLOB/HLOM benchmark JSON; do not infer unmeasured results.

Usage:
 python -m benchmarks.summarize_hlob_hlom omega-ci-results.json
 python -m benchmarks.summarize_hlob_hlom omega-ci-results.json --output summary.md

HLOM includes parity while HLOB does not; a size winner is not a
feature-equivalent winner. Summary only covers inputs present in the JSON.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def summarize(report: dict) -> str:
    results = report.get("results")
    if not isinstance(results, list) or not results:
        raise ValueError("missing benchmark results")
    lines = [
        "# HLOB vs HLOM — measured comparison",
        "",
        "These figures come from the supplied benchmark JSON, not predictions.",
        "HLOM includes GF(256) repair; HLOB does not. Smaller is not necessarily better.",
        "",
        "| Sample | Input (B) | HLOB (B) | HLOM (B) | Smaller archive | HLOB enc (ms) | HLOM enc (ms) |",
        "|---|---:|---:|---:|---|---:|---:|",
    ]
    counts = {"HLOB": 0, "HLOM": 0, "tie": 0}
    for entry in results:
        formats = entry["formats"]
        a, b = formats["HLOB"], formats["HLOM"]
        if not a.get("sha256_roundtrip_ok") or not b.get("sha256_roundtrip_ok"):
            raise ValueError("roundtrip verification failed or missing")
        sa, sb = a["encrypted_bytes_median"], b["encrypted_bytes_median"]
        if not isinstance(sa, (int, float)) or not isinstance(sb, (int, float)):
            raise ValueError("missing encrypted size")
        winner = "HLOB" if sa < sb else "HLOM" if sb < sa else "tie"
        counts[winner] += 1
        filename = str(entry["file"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {filename} | {entry['input_bytes']} | {sa:g} | {sb:g} | "
            f"{winner} | {a['encrypt_ms_median']:g} | {b['encrypt_ms_median']:g} |"
        )
    lines.extend([
        "",
        f"**Archive-size wins:** HLOB {counts['HLOB']}, "
        f"HLOM {counts['HLOM']}, ties {counts['tie']}.",
        "",
        "Limitations: synthetic samples are not representative of arbitrary real files; "
        "timings depend on hardware and runtime; comparison excludes damage-recovery testing.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    markdown = summarize(json.loads(args.report.read_text(encoding="utf-8")))
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
