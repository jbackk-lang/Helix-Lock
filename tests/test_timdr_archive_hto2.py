"""HTO2 regression tests: real Helix cipher, tampering and two erasures."""
import os
import pytest
from helix_pro import generate_key
from helix_pro.timdr_archive_hto2 import pack, unpack, parse

@pytest.mark.parametrize("data",[b"",b"abc"*10000,bytes(range(256))*1000,os.urandom(50000)])
def test_roundtrip(data):
    key=generate_key()
    assert unpack(pack(data,key,block_size=4096),key)==(data,0)

def damage(archive,key,indices):
    bad=bytearray(archive)
    info,payload=parse(archive,key)
    base=len(archive)-len(payload)
    for i in indices:
        d=info["groups"][0]["blocks"][i]
        bad[base+d["offset"]+2]^=0x80
    return bytes(bad)

def test_two_ciphertext_erasures():
    key=generate_key();data=os.urandom(17000)
    archive=pack(data,key,block_size=4096)
    assert unpack(damage(archive,key,[0,1]),key)==(data,2)

def test_three_erasures_fail_closed():
    key=generate_key();archive=pack(os.urandom(17000),key,block_size=4096)
    with pytest.raises(ValueError):unpack(damage(archive,key,[0,1,2]),key)

def test_single_index_copy_corruption():
    key=generate_key();data=b"test"*2000
    archive=bytearray(pack(data,key));archive[12]^=1
    assert unpack(bytes(archive),key)==(data,0)

def test_wrong_key_rejected():
    key=generate_key()
    with pytest.raises(ValueError):unpack(pack(b"secret",key),generate_key())
