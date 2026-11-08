import json
import pytest

from experiments.helix_native_compact import (
    HEADER, decode_compact, encode_compact,
)
from experiments.helix_native_codec import encode_bytes, decode_bytes


@pytest.mark.parametrize("payload", [b"", b"Helix", bytes(range(256)), b"\\x00" * 128])
@pytest.mark.parametrize("sign", (-1, 1))
def test_compact_roundtrip_and_cross_format(payload, sign):
    compact = encode_compact(payload, handedness=sign)
    recovered, decoded_sign = decode_compact(compact)
    assert recovered == payload and decoded_sign == sign
    assert decode_bytes(encode_bytes(payload, handedness=sign)) == recovered
    assert len(compact) == HEADER.size + len(payload)


def test_compact_smaller_than_json_phase_samples():
    payload = bytes(range(64))
    assert len(encode_compact(payload)) < len(encode_bytes(payload))


def test_tampered_payload_detected_but_not_authenticated():
    encoded = bytearray(encode_compact(b"HELIX"))
    encoded[-1] ^= 1
    with pytest.raises(ValueError, match="corruption"):
        decode_compact(bytes(encoded))


def test_truncated_and_invalid_sign_rejected():
    encoded = encode_compact(b"data")
    with pytest.raises(ValueError):
        decode_compact(encoded[:-1])
    altered = bytearray(encoded)
    altered[4] = 3
    with pytest.raises(ValueError):
        decode_compact(bytes(altered))


def test_compact_is_not_secret():
    payload = b"PUBLIC INFORMATION"
    encoded = encode_compact(payload)
    assert payload in encoded  # explicit negative control for confidentiality
