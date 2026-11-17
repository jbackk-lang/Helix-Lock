"""Tests for sampled HTO4 predictor selection."""
import os
import pytest
from helix_pro import generate_key
from helix_pro.timdr_archive_fast import choose_mode, pack, unpack

@pytest.mark.parametrize("data",[b"",b"ABCD"*65536,bytes(262144),os.urandom(262144)])
def test_sampled_roundtrip(data):
    key=generate_key()
    assert unpack(pack(data,key),key)==(data,0)

def test_short_inputs_choose_raw():
    assert choose_mode(b"A"*1000)=="raw"

def test_highly_compressible_choose_raw():
    assert choose_mode(bytes(262144))=="raw"

def test_wrong_key_rejected():
    key=generate_key()
    with pytest.raises(ValueError):
        unpack(pack(b"secret"*5000,key),generate_key())
