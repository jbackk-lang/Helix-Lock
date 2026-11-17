"""Regression tests for triple-header HTO3 envelope."""
import os
import pytest
from helix_pro import generate_key
from helix_pro.timdr_archive_hto3 import pack, unpack, HEADER_SIZE, EnvelopeError

@pytest.mark.parametrize("data",[b"",b"abc"*10000,os.urandom(18000)])
def test_roundtrip(data):
    key=generate_key()
    assert unpack(pack(data,key,block_size=4096),key)==(data,0)

@pytest.mark.parametrize("bad_copies",[(0,),(0,1),(1,2)])
def test_two_header_copies_can_be_corrupted(bad_copies):
    key=generate_key();data=b"recovery"*1000
    archive=bytearray(pack(data,key))
    for i in bad_copies:archive[i*HEADER_SIZE]^=0xff
    assert unpack(bytes(archive),key)==(data,0)

def test_three_headers_corrupt_fail_closed():
    key=generate_key();archive=bytearray(pack(b"data",key))
    for i in range(3):archive[i*HEADER_SIZE]^=0xff
    with pytest.raises(EnvelopeError):unpack(bytes(archive),key)

def test_wrong_key_rejected():
    key=generate_key()
    with pytest.raises(EnvelopeError):unpack(pack(b"data",key),generate_key())

def test_payload_truncation_rejected():
    key=generate_key()
    with pytest.raises(EnvelopeError):unpack(pack(b"data",key)[:-1],key)
