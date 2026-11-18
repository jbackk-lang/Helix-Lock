"""Test measured HLOB/HLOM JSON summary, including integrity gating."""
import pytest

from benchmarks.summarize_hlob_hlom import summarize


def report():
    return {"results": [
        {"file": "gradient.bin", "input_bytes": 100,
         "formats": {
             "HLOB": {"sha256_roundtrip_ok": True,
                      "encrypted_bytes_median": 45, "encrypt_ms_median": 1.2},
             "HLOM": {"sha256_roundtrip_ok": True,
                      "encrypted_bytes_median": 80, "encrypt_ms_median": 2.3}}},
        {"file": "random.bin", "input_bytes": 100,
         "formats": {
             "HLOB": {"sha256_roundtrip_ok": True,
                      "encrypted_bytes_median": 150, "encrypt_ms_median": 1.4},
             "HLOM": {"sha256_roundtrip_ok": True,
                      "encrypted_bytes_median": 120, "encrypt_ms_median": 2.1}}},
    ]}


def test_summarize_uses_actual_input_scores():
    result = summarize(report())
    assert "gradient.bin" in result
    assert "| 100 | 45 | 80 | HLOB |" in result
    assert "| 100 | 150 | 120 | HLOM |" in result
    assert "HLOB 1, HLOM 1, ties 0" in result
    assert "GF(256)" in result


def test_refuse_unverified_roundtrip():
    data = report()
    data["results"][0]["formats"]["HLOB"]["sha256_roundtrip_ok"] = False
    with pytest.raises(ValueError, match="roundtrip"):
        summarize(data)


def test_refuse_empty_report():
    with pytest.raises(ValueError):
        summarize({"results": []})
