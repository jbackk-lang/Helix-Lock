"""HTO4 experimental integration: reversible TIMDR-Omega predictors + HTO3.

This is a predictor experiment, NOT a mathematically validated TIMDR
triple-loop codec. Uses HTO3/HTO2 Helix encryption and GF256 repair.
"""
import struct
import zlib
from . import timdr_archive_hto3 as resilient

MAGIC=b"HTO4"
MODES=("raw","1d","2d","3d")
LAG=4096

def transform(src,mode):
    if mode=="raw":return src
    out=bytearray(len(src))
    for i,v in enumerate(src):
        if mode=="1d":p=src[i-1] if i else 0
        elif mode=="2d":p=src[i-2] if i>=2 else 0
        elif mode=="3d":p=(src[i-LAG]^src[i-1]^src[i-LAG-1]) if i>LAG else (src[i-1] if i else 0)
        else:raise ValueError("unknown mode")
        out[i]=v^p
    return bytes(out)

def inverse(src,mode):
    if mode=="raw":return src
    out=bytearray(len(src))
    for i,v in enumerate(src):
        if mode=="1d":p=out[i-1] if i else 0
        elif mode=="2d":p=out[i-2] if i>=2 else 0
        elif mode=="3d":p=(out[i-LAG]^out[i-1]^out[i-LAG-1]) if i>LAG else (out[i-1] if i else 0)
        else:raise ValueError("unknown mode")
        out[i]=v^p
    return bytes(out)

def pack(data,key,block_size=65536,mode="auto"):
    if mode=="auto":
        candidates=MODES if len(data)>=16384 else MODES[:3]
        # Match the best predictor according to an actual compressed-size
        # estimate; the HTO3 inner codec compresses the transformed data.
        mode=min(candidates,key=lambda m:len(zlib.compress(transform(data,m))))
    if mode not in MODES:raise ValueError("invalid predictor mode")
    transformed=transform(data,mode)
    inner=resilient.pack(transformed,key,block_size=block_size)
    # Mode is authenticated indirectly: changing it makes the inner
    # HTO3 payload still valid, so bind the selector using HMAC.
    import hmac
    header=MAGIC+bytes([MODES.index(mode)])+struct.pack(">Q",len(data))
    tag=hmac.digest(hmac.digest(key,b"HTO4 selector v1","sha256"),header,"sha256")
    return header+tag+inner

def unpack(archive,key):
    import hmac
    if len(archive)<45 or archive[:4]!=MAGIC:raise ValueError("invalid HTO4 header")
    header=archive[:13];tag=archive[13:45]
    expected=hmac.digest(hmac.digest(key,b"HTO4 selector v1","sha256"),header,"sha256")
    if not hmac.compare_digest(tag,expected):raise ValueError("selector authentication failed")
    mode_id=header[4]
    if mode_id>=len(MODES):raise ValueError("invalid predictor")
    expected_len=struct.unpack(">Q",header[5:13])[0]
    transformed,repaired=resilient.unpack(archive[45:],key)
    if len(transformed)!=expected_len:raise ValueError("transformed length mismatch")
    return inverse(transformed,MODES[mode_id]),repaired
