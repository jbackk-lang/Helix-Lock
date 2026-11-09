import os

import pytest
from cryptography.exceptions import InvalidTag

from helix_stream.records import RecordError, RecordOpener, RecordSealer, MAX_PLAINTEXT


def pair():
    key = os.urandom(32)
    salt = os.urandom(4)
    session = os.urandom(16)
    direction = b"client-to-server"
    return (
        RecordSealer(key, salt, session, direction),
        RecordOpener(key, salt, session, direction),
    )


@pytest.mark.parametrize("size", [0, 1, 65535, 65536])
def test_record_roundtrip(size):
    seal, open_record = pair()
    payload = os.urandom(size)
    frame = seal.seal(payload)
    restored, final = open_record.open(frame)
    assert restored == payload
    assert not final
    _, final = open_record.open(seal.seal(final=True))
    assert final


def test_record_rejects_oversized_payload():
    seal, _ = pair()
    with pytest.raises(RecordError, match="maximum"):
        seal.seal(b"x" * (MAX_PLAINTEXT + 1))


def test_record_rejects_wrong_key_and_preserves_sequence():
    seal, _ = pair()
    frame = seal.seal(b"secret")
    wrong = RecordOpener(os.urandom(32), os.urandom(4), os.urandom(16),
                         b"client-to-server")
    with pytest.raises(InvalidTag):
        wrong.open(frame)


def test_record_rejects_tampering_and_metadata_change():
    seal, _ = pair()
    frame = bytearray(seal.seal(b"payload"))
    frame[-1] ^= 1
    _, opener = pair()
    with pytest.raises((InvalidTag, RecordError)):
        opener.open(bytes(frame))


def test_record_rejects_replay_and_out_of_order():
    seal, opener = pair()
    first = seal.seal(b"one")
    second = seal.seal(b"two")
    with pytest.raises(RecordError, match="sequence"):
        opener.open(second)
    assert opener.open(first) == (b"one", False)
    assert opener.open(second) == (b"two", False)
    with pytest.raises(RecordError, match="sequence"):
        opener.open(first)


def test_final_record_closes_both_sides():
    seal, opener = pair()
    final = seal.seal(final=True)
    assert opener.open(final) == (b"", True)
    with pytest.raises(RecordError, match="closed"):
        seal.seal(b"late")
    with pytest.raises(RecordError, match="closed"):
        opener.open(final)


def test_record_rejects_truncation_and_trailing_bytes():
    seal, _ = pair()
    frame = seal.seal(b"payload")
    _, opener = pair()
    with pytest.raises(RecordError):
        opener.open(frame[:-1])
    _, opener = pair()
    with pytest.raises(RecordError, match="length"):
        opener.open(frame + b"x")


def test_direction_is_authenticated():
    key, salt, session = os.urandom(32), os.urandom(4), os.urandom(16)
    seal = RecordSealer(key, salt, session, b"client-to-server")
    opener = RecordOpener(key, salt, session, b"server-to-client")
    with pytest.raises(InvalidTag):
        opener.open(seal.seal(b"direction bound"))
