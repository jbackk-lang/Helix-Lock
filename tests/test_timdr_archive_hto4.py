"""HTO4 predictor + Helix repair integration regression tests."""
import os
import pytest
from helix_pro import generate_key
from helix_pro.timdr_archive_hto4 import pack,unpack,transform,inverse,MODES
from helix_pro.timdr_archive_hto3 import PREFIX_SIZE
from helix_pro.timdr_archive_hto2 import parse

@pytest.mark.parametrize("mode",MODES)
@pytest.mark.parametrize("data",[b"",b"ABCD"*5000,bytes(range(256))*80,os.urandom(19000)])
def test_roundtrip(mode,data):
    key=generate_key()
    assert unpack(pack(data,key,block_size=4096,mode=mode),key)==(data,0)

def test_auto_mode():
    key=generate_key();data=b"XYZ"*10000
    assert unpack(pack(data,key,mode="auto"),key)==(data,0)

def test_two_erasure_repair():
    key=generate_key();data=os.urandom(18000)
    archive=bytearray(pack(data,key,block_size=4096,mode="3d"))
    hto2=bytes(archive[45+PREFIX_SIZE:])
    info,payload=parse(hto2,key)
    base=len(archive)-len(payload)
    for i in (0,1):
        item=info["groups"][0]["blocks"][i]
        archive[base+item["offset"]+3]^=0x80
    assert unpack(bytes(archive),key)==(data,2)

def test_selector_tampering_and_wrong_key():
    key=generate_key();archive=bytearray(pack(b"test"*3000,key))
    archive[4]^=1
    with pytest.raises(ValueError):unpack(bytes(archive),key)
    with pytest.raises(ValueError):unpack(pack(b"secret",key),generate_key())
