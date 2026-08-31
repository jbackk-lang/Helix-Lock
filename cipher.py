"""
helix_pro/cipher.py — rdzen Helix Pro: AES-256-GCM (uwierzytelnione
szyfrowanie z biblioteki `cryptography`, ta sama solidna podstawa co w
oryginalnym helix_lock_cipher.py) w dwoch trybach:

- tryb pliku-klucza: 32 losowe bajty z generate_key() (jak w
  helix_lock_cipher.py) - najsilniejszy wybor, jesli mozesz bezpiecznie
  przechowac plik klucza osobno od zaszyfrowanych danych.
- tryb hasla: derive_key_from_password() uzywa scrypt (parametry N=2**14,
  r=8, p=1 - koszt pamieciowy/czasowy utrudniajacy brute-force, w
  odroznieniu od gologo SHA256(haslo) w starym helix_cipher.py) z losowa
  sola zapisywana razem z zaszyfrowanym plikiem (potrzebna do ponownego
  wyprowadzenia tego samego klucza przy odszyfrowywaniu).

Format pliku (encrypt_file), wszystko binarne, w tej kolejnosci:
  MAGIC (4B "HLXP") | wersja (1B) | tryb (1B: 0x01=klucz, 0x02=haslo)
  | [tylko tryb hasla: sol (16B)] | nonce (12B) | ciphertext+tag (AES-GCM)

AES-GCM sam w sobie uwierzytelnia (tag integralnosci wliczony w
ciphertext przez bibioteke `cryptography`) - kazda zmiana pojedynczego
bajtu ciphertextu, nonce albo AAD powoduje, ze decrypt rzuca wyjatek
zamiast po cichu zwrocic zle dane. To naprawia brak autentykacji w
starym helix_cipher.py (AES-CBC bez HMAC).
"""
from __future__ import annotations

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidTag

MAGIC = b"HLXP"
VERSION = 1
MODE_KEY = b"\x01"
MODE_PASSWORD = b"\x02"

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # 256 bit

# Parametry scrypt - N=2**14 to rozsadny wspolczesny minimum (RFC 7914
# sugeruje N=2**14 dla interaktywnych logowan); wyzsze N = wolniej dla
# atakujacego brute-force, ale tez wolniej dla Ciebie przy kazdym
# odszyfrowaniu - ten kompromis jest jawny tutaj, nie ukryty w kodzie.
SCRYPT_N = 2 ** 14
SCRYPT_R = 8
SCRYPT_P = 1


class HelixProError(Exception):
    """Wspolny wyjatek Helix Pro - zly klucz/haslo, uszkodzony lub
    zmanipulowany plik, albo nieznany format/wersja. Celowo NIE
    rozroznia "zly klucz" od "plik zmanipulowany" w komunikacie wprost
    do wywolujacego kodu (AES-GCM nie pozwala tego odroznic bez
    dodatkowych przeciekow czasowych) - ale samo Python-owe repr()
    wyjatku w testach/logach dev moze pokazac szczegol z ponizszego kodu."""


def generate_key() -> bytes:
    """32 losowe bajty - klucz do trybu pliku-klucza. Przechowuj go
    OSOBNO od zaszyfrowanych danych (inny dysk/nosnik/miejsce) - jesli
    oba leza obok siebie, szyfrowanie nie chroni przed kims, kto ma
    dostep do calego folderu."""
    return AESGCM.generate_key(bit_length=256)


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Wyprowadza 32-bajtowy klucz z hasla przez scrypt (z sola i
    kosztem pamieciowym) - w odroznieniu od starego helix_cipher.py,
    ktory uzywal goleg SHA256(haslo) bez soli (podatne na tablice
    teczowe/rownolegly brute-force wielu hasel naraz) i bez zadnego
    kosztu obliczeniowego (podatne na szybki brute-force)."""
    kdf = Scrypt(salt=salt, length=KEY_SIZE, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(plaintext: bytes, key: bytes, aad: bytes = b"") -> bytes:
    """Szyfruje surowe bajty gotowym 32-bajtowym kluczem (bez naglowka
    trybu/soli - to zadanie encrypt_file/wywolujacego kodu). `aad`
    (additional authenticated data) jest uwierzytelniane, ale NIE
    szyfrowane - uzywane np. przez counter_lock.py, zeby zwiazac licznik
    z ciphertextem bez ujawniania go w tresci."""
    if len(key) != KEY_SIZE:
        raise HelixProError(f"klucz musi miec {KEY_SIZE} bajtow, dostano {len(key)}")
    nonce = os.urandom(NONCE_SIZE)
    ct = AESGCM(key).encrypt(nonce, plaintext, aad or None)
    return nonce + ct


def decrypt_bytes(blob: bytes, key: bytes, aad: bytes = b"") -> bytes:
    if len(key) != KEY_SIZE:
        raise HelixProError(f"klucz musi miec {KEY_SIZE} bajtow, dostano {len(key)}")
    if len(blob) < NONCE_SIZE:
        raise HelixProError("dane za krotkie, brak pelnego nonce")
    nonce, ct = blob[:NONCE_SIZE], blob[NONCE_SIZE:]
    try:
        return AESGCM(key).decrypt(nonce, ct, aad or None)
    except InvalidTag as exc:
        raise HelixProError(
            "nie udalo sie odszyfrowac - zly klucz/haslo albo plik zostal zmanipulowany/uszkodzony"
        ) from exc


def encrypt_file(in_path: str, out_path: str, *, key: bytes | None = None, password: str | None = None) -> None:
    """Szyfruje plik do formatu Helix Pro opisanego w docstringu modulu.
    Podaj dokladnie jedno z: `key` (bytes z generate_key()) albo
    `password` (str - klucz wyprowadzany przez scrypt z losowa sola,
    ktora zostaje zapisana w naglowku pliku wyjsciowego)."""
    if (key is None) == (password is None):
        raise HelixProError("podaj dokladnie jedno z: key, password")

    with open(in_path, "rb") as f:
        plaintext = f.read()

    if key is not None:
        header = MAGIC + bytes([VERSION]) + MODE_KEY
        blob = encrypt_bytes(plaintext, key)
    else:
        salt = os.urandom(SALT_SIZE)
        derived = derive_key_from_password(password, salt)
        header = MAGIC + bytes([VERSION]) + MODE_PASSWORD + salt
        blob = encrypt_bytes(plaintext, derived)

    with open(out_path, "wb") as f:
        f.write(header + blob)


def decrypt_file(in_path: str, out_path: str, *, key: bytes | None = None, password: str | None = None) -> None:
    if (key is None) == (password is None):
        raise HelixProError("podaj dokladnie jedno z: key, password")

    with open(in_path, "rb") as f:
        data = f.read()

    if data[:4] != MAGIC:
        raise HelixProError("nieznany format pliku (brak naglowka Helix Pro)")
    version = data[4]
    if version != VERSION:
        raise HelixProError(f"nieobslugiwana wersja formatu: {version}")
    mode = data[5:6]

    if mode == MODE_KEY:
        if key is None:
            raise HelixProError("ten plik jest w trybie klucza - podaj key, nie password")
        plaintext = decrypt_bytes(data[6:], key)
    elif mode == MODE_PASSWORD:
        if password is None:
            raise HelixProError("ten plik jest w trybie hasla - podaj password, nie key")
        salt = data[6:6 + SALT_SIZE]
        derived = derive_key_from_password(password, salt)
        plaintext = decrypt_bytes(data[6 + SALT_SIZE:], derived)
    else:
        raise HelixProError(f"nieznany tryb w naglowku: {mode!r}")

    with open(out_path, "wb") as f:
        f.write(plaintext)
