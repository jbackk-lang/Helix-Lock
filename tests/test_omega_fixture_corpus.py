"""Deterministic synthetic Omega corpus tests."""
import hashlib

import pytest

from benchmarks.omega_fixture_corpus import corpus, write_corpus


def test_determinism_and_shapes():
    a = corpus(1024, 42)
    assert a == corpus(1024, 42)
    assert set(a) == {
        "random.bin", "gradient.bin", "rows.bin", "rgb-interleaved.bin",
        "mixed-channels.bin", "periodic.bin", "already-compressed.bin",
        "mostly-zeros.bin",
    }
    assert a["random.bin"] != corpus(1024, 43)["random.bin"]
    assert all(len(blob) == 1024 for name, blob in a.items()
               if name != "already-compressed.bin")


def test_manifest_hashes(tmp_path):
    manifest = write_corpus(tmp_path, size=512, seed=17)
    assert len(manifest["files"]) == 8
    for item in manifest["files"]:
        content = (tmp_path / item["filename"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == item["sha256"]


@pytest.mark.parametrize("size", [0, -1])
def test_invalid_size(size):
    with pytest.raises(ValueError):
        corpus(size)
