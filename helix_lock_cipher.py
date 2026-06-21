import os
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE = 32  # 256 bit

def generate_key(path: str):
    key = AESGCM.generate_key(bit_length=256)
    with open(path, "wb") as f:
        f.write(key)
    print(f"[Helix‑Lock] Wygenerowano klucz: {path}")

def load_key(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def encrypt_file(in_path: str, out_path: str, key_path: str):
    key = load_key(key_path)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    with open(in_path, "rb") as f:
        data = f.read()

    ct = aesgcm.encrypt(nonce, data, None)

    with open(out_path, "wb") as f:
        f.write(nonce + ct)

    print(f"[Helix‑Lock] Zaszyfrowano: {in_path} → {out_path}")

def decrypt_file(in_path: str, out_path: str, key_path: str):
    key = load_key(key_path)
    aesgcm = AESGCM(key)

    with open(in_path, "rb") as f:
        blob = f.read()

    nonce = blob[:12]
    ct = blob[12:]

    pt = aesgcm.decrypt(nonce, ct, None)

    with open(out_path, "wb") as f:
        f.write(pt)

    print(f"[Helix‑Lock] Odszyfrowano: {in_path} → {out_path}")

def main():
    if len(sys.argv) < 2:
        print("Użycie:")
        print("  python helix_lock_cipher.py keygen <keyfile>")
        print("  python helix_lock_cipher.py encrypt <in> <out> <keyfile>")
        print("  python helix_lock_cipher.py decrypt <in> <out> <keyfile>")
        return

    cmd = sys.argv[1]

    if cmd == "keygen" and len(sys.argv) == 3:
        generate_key(sys.argv[2])
    elif cmd == "encrypt" and len(sys.argv) == 5:
        encrypt_file(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "decrypt" and len(sys.argv) == 5:
        decrypt_file(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Błędne argumenty.")

if __name__ == "__main__":
    main()
