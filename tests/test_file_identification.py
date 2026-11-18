"""Read-only desktop format recognition; no GUI/display required."""
import pytest

from helix_pro.file_identification import identify_header


@pytest.mark.parametrize("header, label, counter", [
    (b"HLXC\x01" + (7).to_bytes(8, "big"), "CounterLock / HLXC", 7),
    (b"HLOB\x01\x01" + b"x" * 7, "Experimental OBX1 / HLOB", None),
    (b"HLOB\x01\x02" + b"x" * 7, "Experimental OBX1 / HLOB", None),
    (b"HLOM\x01\x01" + b"x" * 7, "Experimental Omega / HLOM", None),
    (b"HLXN" + b"x" * 9, "Helix named / HLXN", None),
    (b"HLXP" + b"x" * 9, "Helix / HLXP", None),
    (b"HLOB\x02\x01", "Unknown / plain file", None),
    (b"HLOM\x01\x09", "Unknown / plain file", None),
    (b"HLXC\x01", "Unknown / plain file", None),
    (b"", "Unknown / plain file", None),
])
def test_identify_header(header, label, counter):
    assert identify_header(header) == (label, counter)
