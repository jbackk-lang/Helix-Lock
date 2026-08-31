#!/usr/bin/env python3
"""
Audyt podwójnego przejścia po pliku:
Oryginał → (kompresja+dekompresja) x2
Porównanie prostych metryk „helisy” (statystyka bajtów).
"""

import sys
import zlib
from collections import Counter
from math import log2


def read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def one_pass(data: bytes) -> bytes:
    """Bezstratne przejście: kompresja + dekompresja (zlib)."""
    comp = zlib.compress(data, level=9)
    decomp = zlib.decompress(comp)
    return decomp


def byte_stats(data: bytes) -> dict:
    """Prosta „helisa” – rozkład bajtów + entropia."""
    cnt = Counter(data)
    total = len(data)
    probs = [c / total for c in cnt.values()]
    entropy = -sum(p * log2(p) for p in probs)
    return {
        "len": total,
        "unique": len(cnt),
        "entropy": entropy,
    }


def main():
    if len(sys.argv) != 2:
        print(f"Użycie: {sys.argv[0]} plik.bin")
        sys.exit(1)

    path = sys.argv[1]
    orig = read_file(path)

    # 1. pierwsze przejście
    pass1 = one_pass(orig)
    # 2. drugie przejście
    pass2 = one_pass(pass1)

    s_orig = byte_stats(orig)
    s_p1 = byte_stats(pass1)
    s_p2 = byte_stats(pass2)

    print("=== Oryginał ===")
    print(s_orig)
    print("=== Po 1 przejściu ===")
    print(s_p1)
    print("=== Po 2 przejściach ===")
    print(s_p2)

    # twarde porównanie bajtów
    print("\nPorównanie bitowe:")
    print("Oryginał == po 1 przejściu:", orig == pass1)
    print("Oryginał == po 2 przejściach:", orig == pass2)


if __name__ == "__main__":
    main()
