import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

def derive_key(password: str) -> bytes:
    return hashlib.sha256(password.encode()).digest()

def pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]) * pad_len

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt_file(path: str, password: str):
    key = derive_key(password)
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv

    with open(path, "rb") as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(pad(plaintext))

    with open(path + ".helix", "wb") as f:
        f.write(iv + ciphertext)

    print(f"[Helix‑Lock] Zaszyfrowano: {path}")

def decrypt_file(path: str, password: str):
    key = derive_key(password)

    with open(path, "rb") as f:
        iv = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(cipher.decrypt(ciphertext))

    out_path = path.replace(".helix", "")
    with open(out_path, "wb") as f:
        f.write(plaintext)

    print(f"[Helix‑Lock] Odszyfrowano: {out_path}")
