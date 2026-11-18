"""File-level OBX1 benchmark smoke tests."""
import json
import zlib

from benchmarks.omega_block_files import measure, main


def test_measure_real_file(tmp_path):
    source = tmp_path / "example.bin"
    data = bytes(range(256)) * 64
    source.write_bytes(data)
    result = measure(source, block_size=1024)
    assert result["roundtrip_ok"]
    assert result["input_bytes"] == len(data)
    assert result["zlib_bytes"] == len(zlib.compress(data, 6))
    assert result["obx1_bytes"] > 0
    assert result["obx1_minus_zlib_bytes"] == result["obx1_bytes"] - result["zlib_bytes"]


def test_empty_file(tmp_path):
    source = tmp_path / "empty"
    source.write_bytes(b"")
    assert measure(source)["roundtrip_ok"]


def test_cli_writes_report(tmp_path, monkeypatch, capsys):
    source = tmp_path / "input.bin"
    source.write_bytes(b"abc" * 300)
    output = tmp_path / "result.json"
    monkeypatch.setattr("sys.argv", ["omega_block_files", str(source), "--output", str(output)])
    main()
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["results"][0]["roundtrip_ok"]
    assert report["format"] == "OBX1 experimental unencrypted"
