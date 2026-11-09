import os

import pytest
from cryptography.exceptions import InvalidTag

from helix_stream.records import RecordError, RecordOpener, RecordSealer, MAX_PLAINTEXT


def pair():
    key, salt, session = os.urandom(32), os.urandom(4), os.urandom(16)
    direction = b"client-to-server"
    return (
        RecordSealer(key, salt, session, direction),
        RecordOpener(key, salt, session, direction),
        key, salt, session, direction,
    )


@pytest.mark.parametrize("size", [0, 1, 65535, 65536])
def test_record_roundtrip(size):
    seal, opener, *_ = pair()
    payload = os.urandom(size)
    assert opener.open(seal.seal(payload)) == (payload, False)
    assert opener.open(seal.seal(final=True)) == (b"", True)


def test_record_rejects_oversized_payload():
    seal, *_ = pair()
    with pytest.raises(RecordError, match="maximum"):
        seal.seal(b"x" * (MAX_PLAINTEXT + 1))


def test_record_rejects_wrong_key():
    seal, _, _, salt, session, direction = pair()
    frame = seal.seal(b"secret")
    wrong = RecordOpener(os.urandom(32), salt, session, direction)
    with pytest.raises(InvalidTag):
        wrong.open(frame)


def test_record_rejects_tampering():
    seal, opener, *_ = pair()
    frame = bytearray(seal.seal(b"payload"))
    frame[-1] ^= 1
    with pytest.raises(InvalidTag):
        opener.open(bytes(frame))


def test_record_rejects_replay_and_out_of_order():
    seal, opener, *_ = pair()
    first, second = seal.seal(b"one"), seal.seal(b"two")
    with pytest.raises(RecordError, match="sequence"):
        opener.open(second)
    assert opener.open(first) == (b"one", False)
    assert opener.open(second) == (b"two", False)
    with pytest.raises(RecordError, match="sequence"):
        opener.open(first)


def test_final_record_closes_both_sides():
    seal, opener, *_ = pair()
    final = seal.seal(final=True)
    assert opener.open(final) == (b"", True)
    with pytest.raises(RecordError, match="closed"):
        seal.seal(b"late")
    with pytest.raises(RecordError, match="closed"):
        opener.open(final)


def test_record_rejects_truncation_and_trailing_bytes():
    seal, opener, *_ = pair()
    frame = seal.seal(b"payload")
    with pytest.raises(RecordError):
        opener.open(frame[:-1])
    seal, opener, *_ = pair()
    frame = seal.seal(b"payload")
    with pytest.raises(RecordError, match="length"):
        opener.open(frame + b"x")


def test_direction_is_authenticated():
    key, salt, session = os.urandom(32), os.urandom(4), os.urandom(16)
    seal = RecordSealer(key, salt, session, b"client-to-server")
    opener = RecordOpener(key, salt, session, b"server-to-client")
    with pytest.raises(InvalidTag):
        opener.open(seal.seal(b"direction bound"))
