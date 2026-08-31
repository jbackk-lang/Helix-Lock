import json
import base64
import hashlib
import hmac

MAGIC = b"HLX1"

def sign(data: bytes, key: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()

def encrypt_with_counter(data: bytes, key: bytes, counter: int = 0) -> bytes:
    header = {
        "counter": counter
    }
    header_bytes = json.dumps(header).encode()
    payload = base64.b64encode(data)

    signed = sign(header_bytes + payload, key)

    return MAGIC + signed + b"|" + header_bytes + b"|" + payload


def decrypt_with_counter(blob: bytes, key: bytes):
    assert blob.startswith(MAGIC)
    blob = blob[len(MAGIC):]

    sig, header_bytes, payload = blob.split(b"|", 2)

    # verify signature
    expected = sign(header_bytes + payload, key)
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Invalid signature")

    header = json.loads(header_bytes.decode())
    counter = header["counter"]

    # increment counter
    header["counter"] += 1
    new_header_bytes = json.dumps(header).encode()
    new_sig = sign(new_header_bytes + payload, key)

    # return decrypted data + updated blob
    data = base64.b64decode(payload)
    updated_blob = MAGIC + new_sig + b"|" + new_header_bytes + b"|" + payload

    return data, counter, updated_blob
