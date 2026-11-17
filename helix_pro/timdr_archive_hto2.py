"""HTO2: experimental Helix AES-GCM archive with 2-erasure GF(256) repair."""
import hashlib, hmac, json, os, struct, zlib
from .cipher import encrypt_bytes, decrypt_bytes

MAGIC=b"HTO2"
COEFS=(1,2,4,8)

def mul(a,b):
    v=0
    while b:
        if b&1:v^=a
        a<<=1
        if a&256:a^=0x11d
        b>>=1
    return v

TABLES=[bytes(mul(c,x) for x in range(256)) for c in COEFS]

def xor_into(dst,src,table=None):
    if table:src=src.translate(table)
    for i,b in enumerate(src):dst[i]^=b

def parity(blocks):
    width=max(map(len,blocks))
    p,q=bytearray(width),bytearray(width)
    for i,b in enumerate(blocks):
        xor_into(p,b);xor_into(q,b,TABLES[i])
    return bytes(p),bytes(q)

def index_key(key):
    if len(key)!=32:raise ValueError("key must be 32 bytes")
    return hmac.digest(key,b"HTO2 authenticated index", "sha256")

def pack(data,key,block_size=65536):
    index_key(key)
    if not 1<=block_size<=1048576:raise ValueError("bad block size")
    chunks=[data[i:i+block_size] for i in range(0,len(data),block_size)]
    payload=bytearray();groups=[]
    for j in range(0,len(chunks),4):
        raw=chunks[j:j+4]
        encrypted=[encrypt_bytes(zlib.compress(b),key,aad=b"HTO2:data") for b in raw]
        blocks=encrypted+list(parity(encrypted));desc=[]
        for b in blocks:
            desc.append(dict(offset=len(payload),length=len(b),sha256=hashlib.sha256(b).hexdigest()))
            payload.extend(b)
        groups.append(dict(lengths=list(map(len,raw)),blocks=desc))
    meta=json.dumps(dict(version=2,total=len(data),groups=groups),sort_keys=True,separators=(",",":")).encode()
    if len(meta)>32*1024*1024:raise ValueError("index too large")
    tag=hmac.digest(index_key(key),meta,"sha256")
    return MAGIC+struct.pack(">I",len(meta))+(meta+tag)*2+payload

def parse(archive,key):
    if len(archive)<8 or archive[:4]!=MAGIC:raise ValueError("bad header")
    n=struct.unpack(">I",archive[4:8])[0]
    if n>32*1024*1024 or len(archive)<8+2*(n+32):raise ValueError("bad index size")
    info=None
    for i in range(2):
        off=8+i*(n+32);meta=archive[off:off+n];tag=archive[off+n:off+n+32]
        if hmac.compare_digest(hmac.digest(index_key(key),meta,"sha256"),tag):
            info=json.loads(meta);break
    if info is None or info.get("version")!=2:raise ValueError("index authentication failed")
    return info,memoryview(archive)[8+2*(n+32):]

def unpack(archive,key):
    info,payload=parse(archive,key);out=bytearray();repairs=0
    for group in info["groups"]:
        lengths=group["lengths"];desc=group["blocks"];k=len(lengths)
        if not 1<=k<=4 or len(desc)!=k+2:raise ValueError("bad group")
        blocks=[]
        for d in desc:
            off,n=d["offset"],d["length"]
            if not isinstance(off,int) or not isinstance(n,int) or off<0 or n<0 or off+n>len(payload):
                raise ValueError("bad block bounds")
            b=bytes(payload[off:off+n])
            blocks.append(b if hashlib.sha256(b).hexdigest()==d["sha256"] else None)
        missing=[i for i in range(k) if blocks[i] is None]
        if missing:
            if len(missing)>2:raise ValueError("too many damaged segments")
            width=max(d["length"] for d in desc[:k])
            p=bytearray(blocks[k] if blocks[k] is not None else bytes(width))
            q=bytearray(blocks[k+1] if blocks[k+1] is not None else bytes(width))
            for i in range(k):
                if blocks[i] is not None:
                    if blocks[k] is not None:xor_into(p,blocks[i])
                    if blocks[k+1] is not None:xor_into(q,blocks[i],TABLES[i])
            if len(missing)==1:
                i=missing[0]
                if blocks[k] is not None:recovered=bytes(p)
                elif blocks[k+1] is not None:
                    inv=next(x for x in range(1,256) if mul(x,COEFS[i])==1)
                    recovered=bytes(q).translate(bytes(mul(inv,x) for x in range(256)))
                else:raise ValueError("parity unavailable")
                blocks[i]=recovered[:desc[i]["length"]]
            else:
                if blocks[k] is None or blocks[k+1] is None:raise ValueError("parity unavailable")
                a,b=missing
                inv=next(x for x in range(1,256) if mul(x,COEFS[a]^COEFS[b])==1)
                aa=bytes(q[j]^mul(COEFS[b],p[j]) for j in range(width)).translate(bytes(mul(inv,x) for x in range(256)))
                bb=bytes(p[j]^aa[j] for j in range(width))
                blocks[a]=aa[:desc[a]["length"]];blocks[b]=bb[:desc[b]["length"]]
            for i in missing:
                if hashlib.sha256(blocks[i]).hexdigest()!=desc[i]["sha256"]:
                    raise ValueError("repair verification failed")
            repairs+=len(missing)
        for i in range(k):
            try:raw=zlib.decompress(decrypt_bytes(blocks[i],key,aad=b"HTO2:data"))
            except Exception as exc:raise ValueError("ciphertext authentication failed") from exc
            if len(raw)!=lengths[i]:raise ValueError("bad decoded length")
            out.extend(raw)
    if len(out)!=info["total"]:raise ValueError("bad total length")
    return bytes(out),repairs
