import json
import os

import pytest

from experiments.helix_native_codec import (
    encode_bytes, decode_bytes, encode_file, decode_file,
)


@pytest.mark.parametrize("payload", [b"", b"Helix", bytes(range(256)), b"\\x00"*128])
@pytest.mark.parametrize("handedness", [-1, 1])
def test_byte_roundtrip(payload, handedness):
    assert decode_bytes(encode_bytes(payload, handedness=handedness)) == payload


def test_real_file_roundtrip(tmp_path):
    source = tmp_path / "input.bin"
    encoded = tmp_path / "phase.json"
    output = tmp_path / "output.bin"
    source.write_bytes(os.urandom(1024))
    encode_file(source, encoded)
    decode_file(encoded, output)
    assert output.read_bytes() == source.read_bytes()


def test_detects_modified_payload_phase():
    doc = json.loads(encode_bytes(b"hello"))
    doc["records"][0][1] = [x + 3.141592653589793 / 2 for x in doc["records"][0][1]]
    with pytest.raises(ValueError, match="corruption"):
        decode_bytes(json.dumps(doc).encode())


def test_missing_record_rejected():
    doc = json.loads(encode_bytes(b"hello"))
    doc["records"].pop()
    with pytest.raises(ValueError, match="record count"):
        decode_bytes(json.dumps(doc).encode())


def test_bad_geometry_rejected():
    with pytest.raises(ValueError):
        encode_bytes(b"abc", sensors=1)


def test_does_not_write_failed_decode(tmp_path):
    source = tmp_path / "corrupt.json"
    target = tmp_path / "output.bin"
    source.write_bytes(b"not-json")
    with pytest.raises(ValueError):
        decode_file(source, target)
    assert not target.exists()
