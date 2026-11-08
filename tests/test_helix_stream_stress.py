"""Streaming HNS1 stress tests: large files, bounded memory and crash safety."""
import multiprocessing
import os
from pathlib import Path
import tracemalloc

import pytest

from experiments.helix_stream_envelope import encrypt_file, decrypt_file


def _kill_during_replace(source, target, key):
    from unittest.mock import patch
    def crash(*args):
        os._exit(91)
    with patch("experiments.helix_stream_envelope.os.replace", side_effect=crash):
        encrypt_file(source, target, key)


def test_process_crash_before_replace_preserves_target(tmp_path):
    source = tmp_path / "input"
    target = tmp_path / "target"
    source.write_bytes(os.urandom(256 * 1024))
    target.write_bytes(b"old-safe-content")
    proc = multiprocessing.Process(target=_kill_during_replace,
                                   args=(source, target, os.urandom(32)))
    proc.start()
    proc.join(timeout=15)
    if proc.is_alive():
        proc.terminate()
        proc.join()
        pytest.fail("worker hung")
    assert proc.exitcode == 91
    assert target.read_bytes() == b"old-safe-content"


def test_multimegabyte_roundtrip_bounded_python_heap(tmp_path):
    source = tmp_path / "large-input"
    encrypted = tmp_path / "large-encrypted"
    restored = tmp_path / "large-restored"
    # 12 MiB, many 64 KiB chunks.
    with source.open("wb") as out:
        for i in range(192):
            out.write(bytes([i % 256]) * 65536)
    key = os.urandom(32)
    tracemalloc.start()
    try:
        encrypt_file(source, encrypted, key)
        decrypt_file(encrypted, restored, key)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 8 * 1024 * 1024
    assert restored.stat().st_size == source.stat().st_size
    with source.open("rb") as a, restored.open("rb") as b:
        while True:
            x = a.read(65536)
            y = b.read(65536)
            assert x == y
            if not x:
                break


def test_reject_missing_final_record_preserves_existing_target(tmp_path):
    source, encrypted, target = [tmp_path / x for x in ("source", "encrypted", "target")]
    source.write_bytes(os.urandom(180000))
    target.write_bytes(b"old")
    key = os.urandom(32)
    encrypt_file(source, encrypted, key)
    with encrypted.open("r+b") as out:
        out.truncate(out.seek(0, 2) - 40)
    with pytest.raises(ValueError):
        decrypt_file(encrypted, target, key)
    assert target.read_bytes() == b"old"
