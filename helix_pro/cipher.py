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

DRUGI FORMAT (2026-08) - encrypt_file_with_name()/decrypt_bytes_with_name()/
decrypt_file_with_name(), MAGIC "HLXN" (osobny od "HLXP" powyzej, zeby
oba formaty byly jednoznacznie rozrozniane naglowkiem, nigdy pomylone):
zapisuje oryginalna nazwe pliku (basename, np. "zdjecie.jpg") WEWNATRZ
zaszyfrowanej tresci, zaraz przed samymi danymi. Powod: plik `.helixpro`
moze zostac przeniesiony/przeslany/przemianowany zanim ktos go odszyfruje
(np. wyslany mailem, sciagniety przez przegladarke, ktora mangluje
nazwy) - bez tego mechanizmu odszyfrowanie nie ma jak wiedziec, jakie
rozszerzenie/typ miala oryginalna zawartosc, wiec system operacyjny nie
rozpozna typu odtworzonego pliku (Windows okresla typ WYLACZNIE po
rozszerzeniu). Z tym mechanizmem oryginalna nazwa (a wiec i rozszerzenie)
wraca zawsze poprawnie, niezaleznie od tego, jak zostal nazwany sam plik
zaszyfrowany. Uzywane domyslnie przez helix_pro_gui.py.
"""
from __future__ import annotations

import gzip
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidTag

MAGIC = b"HLXP"
MAGIC_NAMED = b"HLXN"
VERSION = 1
MODE_KEY = b"\x01"
MODE_PASSWORD = b"\x02"

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # 256 bit
NAME_LEN_MAX = 255  # dlugosc pola-dlugosci nazwy to 1 bajt (0-255)

# Flaga kompresji tresci w formacie "z nazwa" (1 bajt, zaraz po nazwie,
# PRZED danymi) - gzip, bo to najpopularniejszy/najbardziej przenosny
# format kompresji w standardowej bibliotece Pythona (kazdy inny program
# na swiecie tez go rozpozna, w odroznieniu od np. surowego zlib bez
# naglowka). "Popularny wybor" byl wprost tym, o co poproszono.
COMPRESS_NONE = 0
COMPRESS_GZIP = 1

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


def detect_format(path: str) -> str:
    """Zwraca 'named' (encrypt_file_with_name), 'plain' (encrypt_file)
    albo 'unknown' na podstawie 4-bajtowego naglowka pliku - bez klucza
    ani hasla, wiec mozna wywolac PRZED ich podaniem (np. zeby GUI od
    razu wiedzialo, ktorej sciezki odszyfrowania uzyc)."""
    with open(path, "rb") as f:
        magic = f.read(4)
    if magic == MAGIC_NAMED:
        return "named"
    if magic == MAGIC:
        return "plain"
    return "unknown"


def encrypt_file_with_name(
    in_path: str,
    out_path: str,
    *,
    key: bytes | None = None,
    password: str | None = None,
    compress: bool = True,
) -> None:
    """Jak encrypt_file(), ale dodatkowo zapisuje oryginalna nazwe pliku
    (tylko basename z in_path, nie pelna sciezke) WEWNATRZ zaszyfrowanej
    tresci - patrz "DRUGI FORMAT" w docstringu modulu. Uzyj razem z
    decrypt_bytes_with_name()/decrypt_file_with_name().

    `compress=True` (domyslnie) probuje gzip PRZED szyfrowaniem - "smart":
    uzyty jest tylko wtedy, gdy faktycznie zmniejsza dane (porownanie
    dlugosci po kompresji vs przed). Dla juz skompresowanych formatow
    (jpg, mp4, zip, ...) gzip zwykle NIE pomaga (czasem lekko powieksza),
    wiec w takim przypadku zapisywane sa dane surowe - nigdy nie
    powiekszamy pliku wynikowego przez sama probe kompresji. Ustaw
    compress=False, zeby pominac probe w ogole (np. gdy wiesz z gory,
    ze plik jest juz skompresowany, i chcesz oszczedzic czas na probie)."""
    if (key is None) == (password is None):
        raise HelixProError("podaj dokladnie jedno z: key, password")

    original_name = os.path.basename(in_path)
    name_bytes = original_name.encode("utf-8")
    if len(name_bytes) > NAME_LEN_MAX:
        raise HelixProError(
            f"nazwa pliku '{original_name}' jest za dluga ({len(name_bytes)} bajtow UTF-8, limit {NAME_LEN_MAX}) "
            "dla trybu z zachowana nazwa - uzyj encrypt_file() zamiast tego"
        )

    with open(in_path, "rb") as f:
        content = f.read()

    compress_flag = COMPRESS_NONE
    if compress:
        compressed = gzip.compress(content, compresslevel=9)
        if len(compressed) < len(content):
            compress_flag = COMPRESS_GZIP
            content = compressed
        # w przeciwnym razie zostaje content = surowe dane, flag = NONE -
        # kompresja nigdy nie powieksza pliku wynikowego wzgledem braku kompresji

    payload = bytes([len(name_bytes)]) + name_bytes + bytes([compress_flag]) + content

    if key is not None:
        header = MAGIC_NAMED + bytes([VERSION]) + MODE_KEY
        blob = encrypt_bytes(payload, key)
    else:
        salt = os.urandom(SALT_SIZE)
        derived = derive_key_from_password(password, salt)
        header = MAGIC_NAMED + bytes([VERSION]) + MODE_PASSWORD + salt
        blob = encrypt_bytes(payload, derived)

    with open(out_path, "wb") as f:
        f.write(header + blob)


def decrypt_bytes_with_name(in_path: str, *, key: bytes | None = None, password: str | None = None) -> tuple[str, bytes]:
    """Odczytuje i odszyfrowuje plik z formatu "z nazwa" (MAGIC_NAMED),
    ZWRACA (oryginalna_nazwa, tresc) BEZ zapisywania niczego na dysk -
    decyzja gdzie zapisac (i czy nadpisac istniejacy plik) zostaje
    wywolujacemu kodowi. To dlatego GUI moze najpierw poznac odtworzona
    nazwe/rozszerzenie, a dopiero potem zapytac uzytkownika o katalog -
    patrz helix_pro_gui.py."""
    if (key is None) == (password is None):
        raise HelixProError("podaj dokladnie jedno z: key, password")

    with open(in_path, "rb") as f:
        data = f.read()

    if data[:4] != MAGIC_NAMED:
        raise HelixProError(
            "ten plik nie ma zapisanej oryginalnej nazwy (MAGIC != HLXN) - "
            "uzyj detect_format() zeby sprawdzic format, albo decrypt_file() dla starego formatu"
        )
    version = data[4]
    if version != VERSION:
        raise HelixProError(f"nieobslugiwana wersja formatu: {version}")
    mode = data[5:6]

    if mode == MODE_KEY:
        if key is None:
            raise HelixProError("ten plik jest w trybie klucza - podaj key, nie password")
        payload = decrypt_bytes(data[6:], key)
    elif mode == MODE_PASSWORD:
        if password is None:
            raise HelixProError("ten plik jest w trybie hasla - podaj password, nie key")
        salt = data[6:6 + SALT_SIZE]
        derived = derive_key_from_password(password, salt)
        payload = decrypt_bytes(data[6 + SALT_SIZE:], derived)
    else:
        raise HelixProError(f"nieznany tryb w naglowku: {mode!r}")

    if not payload:
        raise HelixProError("odszyfrowana tresc jest pusta - brak nawet pola dlugosci nazwy, plik uszkodzony")
    name_len = payload[0]
    name_bytes = payload[1:1 + name_len]
    if len(name_bytes) != name_len:
        raise HelixProError("odszyfrowana tresc jest za krotka wzgledem zadeklarowanej dlugosci nazwy - plik uszkodzony")
    original_name = os.path.basename(name_bytes.decode("utf-8"))  # basename tez tutaj - obrona w glab
    if not original_name:
        raise HelixProError("odtworzona nazwa pliku jest pusta po oczyszczeniu")

    rest = payload[1 + name_len:]
    if not rest:
        raise HelixProError("odszyfrowana tresc jest za krotka - brak nawet bajtu flagi kompresji, plik uszkodzony")
    compress_flag, content = rest[0], rest[1:]
    if compress_flag == COMPRESS_GZIP:
        try:
            content = gzip.decompress(content)
        except OSError as exc:  # gzip rzuca OSError/BadGzipFile na uszkodzonych danych
            raise HelixProError(f"nie udalo sie zdekompresowac tresci (gzip) - plik uszkodzony: {exc}") from exc
    elif compress_flag != COMPRESS_NONE:
        raise HelixProError(f"nieznana flaga kompresji w naglowku: {compress_flag}")

    return original_name, content


def decrypt_file_with_name(in_path: str, out_dir: str, *, key: bytes | None = None, password: str | None = None) -> str:
    """Wygodny wrapper nad decrypt_bytes_with_name(): zapisuje odzyskana
    tresc w out_dir pod odtworzona nazwa (z poprawnym rozszerzeniem) i
    zwraca pelna sciezke zapisanego pliku. NADPISUJE bez pytania, jesli
    plik juz istnieje pod ta nazwa - kod wywolujacy z GUI, ktory chce
    zapytac uzytkownika, powinien uzyc decrypt_bytes_with_name()
    bezposrednio i samemu zapisac plik po sprawdzeniu os.path.exists()."""
    original_name, content = decrypt_bytes_with_name(in_path, key=key, password=password)
    out_path = os.path.join(out_dir, original_name)
    with open(out_path, "wb") as f:
        f.write(content)
    return out_path
