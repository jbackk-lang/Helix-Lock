"""HLOB/HLOM encrypted comparison smoke tests."""
import json

import pytest

from benchmarks.compare_hlob_hlom import measure, main


@pytest.mark.parametrize("data", [b"", b"ABCD" * 300, bytes(range(256)) * 8])
def test_both_formats_restore_exact_bytes(tmp_path, data):
    source = tmp_path / "source.bin"
    source.write_bytes(data)
    result = measure(source, repeats=1)
    assert result["input_bytes"] == len(data)
    assert set(result["formats"]) == {"HLOB", "HLOM"}
    for item in result["formats"].values():
        assert item["sha256_roundtrip_ok"]
        assert item["encrypted_bytes_median"] > 0
        assert len(item["encrypt_ms_samples"]) == 1
        assert len(item["decrypt_ms_samples"]) == 1
    assert result["formats"]["HLOM"]["repaired_blocks"] == [0]
    assert result["formats"]["HLOB"]["repaired_blocks"] is None


def test_invalid_repeat_count(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"test")
    with pytest.raises(ValueError):
        measure(source, repeats=0)


def test_cli_json(tmp_path, monkeypatch, capsys):
    source = tmp_path / "source.bin"
    source.write_bytes(b"ABC" * 100)
    destination = tmp_path / "results.json"
    monkeypatch.setattr("sys.argv", [
        "compare_hlob_hlom", str(source), "--repeats", "1",
        "--output", str(destination),
    ])
    main()
    report = json.loads(destination.read_text(encoding="utf-8"))
    assert report["results"][0]["formats"]["HLOB"]["sha256_roundtrip_ok"]
    assert report["results"][0]["formats"]["HLOM"]["sha256_roundtrip_ok"]
