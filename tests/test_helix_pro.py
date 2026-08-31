"""
test_helix_pro.py — pierwsze testy w tym repo (wczesniej Helix-Lock nie
mial ani jednego pliku testowego). Skupione na tym, co odroznia Helix
Pro od oryginalu: (a) payload jest FAKTYCZNIE zaszyfrowany (nie tylko
zakodowany base64 jak w starym HLX1.py), (b) manipulacja
ciphertextem/AAD/licznikiem jest wykrywana, (c) oba tryby (plik-klucza,
haslo) daja poprawny round-trip, (d) zle haslo/klucz jest odrzucane.
"""
import base64
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from helix_pro.cipher import (
    generate_key,
    derive_key_from_password,
    encrypt_bytes,
    decrypt_bytes,
    encrypt_file,
    decrypt_file,
    encrypt_file_with_name,
    decrypt_bytes_with_name,
    decrypt_file_with_name,
    detect_format,
    HelixProError,
)
from helix_pro.counter_lock import CounterLock


# ── cipher.py: tryb klucza ───────────────────────────────────────────

def test_encrypt_decrypt_bytes_roundtrip_with_key():
    key = generate_key()
    data = b"tajna tresc Helix Pro"
    blob = encrypt_bytes(data, key)
    assert decrypt_bytes(blob, key) == data


def test_ciphertext_is_not_just_base64_of_plaintext():
    """Regresja wprost przeciwko bledowi z HLX1.py: upewnij sie, ze
    zaszyfrowany blob NIE jest zwyklym base64 oryginalu (co by oznaczalo,
    ze 'szyfrowanie' to tylko kodowanie)."""
    key = generate_key()
    data = b"latwa do rozpoznania tresc XYZ123"
    blob = encrypt_bytes(data, key)
    assert base64.b64encode(data) not in blob
    assert data not in blob


def test_decrypt_with_wrong_key_raises():
    key_a, key_b = generate_key(), generate_key()
    blob = encrypt_bytes(b"sekret", key_a)
    with pytest.raises(HelixProError):
        decrypt_bytes(blob, key_b)


def test_tampered_ciphertext_is_rejected():
    key = generate_key()
    blob = bytearray(encrypt_bytes(b"nietykana tresc", key))
    blob[-1] ^= 0xFF  # zmieniamy ostatni bajt (tag uwierzytelniajacy)
    with pytest.raises(HelixProError):
        decrypt_bytes(bytes(blob), key)


def test_aad_mismatch_is_rejected():
    key = generate_key()
    blob = encrypt_bytes(b"tresc z aad", key, aad=b"kontekst-a")
    with pytest.raises(HelixProError):
        decrypt_bytes(blob, key, aad=b"kontekst-b")


# ── cipher.py: tryb hasla ────────────────────────────────────────────

def test_derive_key_from_password_is_deterministic_for_same_salt():
    salt = os.urandom(16)
    k1 = derive_key_from_password("haslo123", salt)
    k2 = derive_key_from_password("haslo123", salt)
    assert k1 == k2
    assert len(k1) == 32


def test_derive_key_from_password_differs_for_different_salt():
    k1 = derive_key_from_password("haslo123", os.urandom(16))
    k2 = derive_key_from_password("haslo123", os.urandom(16))
    assert k1 != k2


# ── cipher.py: encrypt_file/decrypt_file (oba tryby, na plikach) ────

def test_encrypt_decrypt_file_roundtrip_key_mode(tmp_path):
    key = generate_key()
    src = tmp_path / "dane.txt"
    src.write_bytes(b"zawartosc pliku do ochrony")
    enc = tmp_path / "dane.helixpro"
    dec = tmp_path / "dane.odzyskane.txt"

    encrypt_file(str(src), str(enc), key=key)
    assert enc.read_bytes() != src.read_bytes()
    decrypt_file(str(enc), str(dec), key=key)
    assert dec.read_bytes() == src.read_bytes()


def test_encrypt_decrypt_file_roundtrip_password_mode(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_bytes(b"zawartosc chroniona haslem")
    enc = tmp_path / "dane.helixpro"
    dec = tmp_path / "dane.odzyskane.txt"

    encrypt_file(str(src), str(enc), password="bardzo-tajne-haslo")
    decrypt_file(str(enc), str(dec), password="bardzo-tajne-haslo")
    assert dec.read_bytes() == src.read_bytes()


def test_encrypt_file_password_mode_uses_random_salt_each_time(tmp_path):
    """Ta sama tresc + to samo haslo, zaszyfrowane dwa razy, musza dac
    ROZNE pliki wyjsciowe (losowa sol + losowy nonce za kazdym razem) -
    inaczej te sama para plaintext/haslo zawsze dawalaby ten sam
    ciphertext, co ulatwia atakujacemu wykrywanie powtorzen."""
    src = tmp_path / "dane.txt"
    src.write_bytes(b"ta sama tresc")
    enc1, enc2 = tmp_path / "a.helixpro", tmp_path / "b.helixpro"
    encrypt_file(str(src), str(enc1), password="haslo")
    encrypt_file(str(src), str(enc2), password="haslo")
    assert enc1.read_bytes() != enc2.read_bytes()


def test_decrypt_file_wrong_password_raises(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_bytes(b"cos tajnego")
    enc = tmp_path / "dane.helixpro"
    encrypt_file(str(src), str(enc), password="wlasciwe-haslo")
    with pytest.raises(HelixProError):
        decrypt_file(str(enc), str(tmp_path / "out.txt"), password="zle-haslo")


def test_decrypt_file_mode_mismatch_raises_clear_error(tmp_path):
    """Plik zaszyfrowany trybem klucza, probowany do odszyfrowania
    haslem (i odwrotnie) - powinien dac jasny blad, nie cichy zly wynik."""
    key = generate_key()
    src = tmp_path / "dane.txt"
    src.write_bytes(b"tresc")
    enc = tmp_path / "dane.helixpro"
    encrypt_file(str(src), str(enc), key=key)
    with pytest.raises(HelixProError):
        decrypt_file(str(enc), str(tmp_path / "out.txt"), password="cokolwiek")


def test_encrypt_file_requires_exactly_one_of_key_or_password(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_bytes(b"tresc")
    with pytest.raises(HelixProError):
        encrypt_file(str(src), str(tmp_path / "out.helixpro"))
    with pytest.raises(HelixProError):
        encrypt_file(
            str(src), str(tmp_path / "out.helixpro"),
            key=generate_key(), password="haslo",
        )


# ── counter_lock.py: naprawiony HLX1 ─────────────────────────────────

def test_counter_lock_roundtrip_returns_data_and_counter():
    lock = CounterLock(generate_key())
    blob = lock.lock(b"wiadomosc", counter=0)
    data, counter = lock.unlock(blob)
    assert data == b"wiadomosc"
    assert counter == 0


def test_counter_lock_payload_is_actually_encrypted_not_base64():
    """Ten sam blad co w oryginalnym HLX1.py, teraz sprawdzony wprost
    dla CounterLock: zakodowany blob nie moze zawierac base64 oryginalu."""
    lock = CounterLock(generate_key())
    data = b"rozpoznawalna-tresc-ABC"
    blob = lock.lock(data, counter=0)
    assert base64.b64encode(data) not in blob
    assert data not in blob


def test_counter_lock_unlock_and_advance_increments_counter():
    lock = CounterLock(generate_key())
    blob = lock.lock(b"wiadomosc", counter=0)
    data, counter, next_blob = lock.unlock_and_advance(blob)
    assert counter == 0
    data2, counter2 = lock.unlock(next_blob)
    assert data2 == b"wiadomosc"
    assert counter2 == 1


def test_counter_lock_rejects_rolled_back_counter_in_header():
    """Sedno naprawy: licznik jest AAD, wiec podmiana samego naglowka z
    licznikiem (bez ponownego zaszyfrowania) musi uniewaznic caly blob -
    to jest dokladnie atak 'cofniecia licznika', przed ktorym HLX1.py
    mial chronic (podpis HMAC), ale ktory tutaj jest silniej zwiazany
    (AEAD zamiast osobnego HMAC nad jawnym base64)."""
    lock = CounterLock(generate_key())
    blob = bytearray(lock.lock(b"wiadomosc", counter=5))

    # naglowek: MAGIC(4) + wersja(1) + counter(8) -- podmieniamy licznik na 0
    import struct
    tampered_counter = struct.pack(">Q", 0)
    blob[5:13] = tampered_counter

    with pytest.raises(HelixProError):
        lock.unlock(bytes(blob))


def test_counter_lock_different_keys_cannot_unlock_each_others_blob():
    lock_a, lock_b = CounterLock(generate_key()), CounterLock(generate_key())
    blob = lock_a.lock(b"wiadomosc", counter=0)
    with pytest.raises(HelixProError):
        lock_b.unlock(blob)


# ── cipher.py: format "z nazwa" (encrypt_file_with_name / decrypt_*_with_name) ──
# Naprawia zgloszony problem: przy odtwarzaniu (deszyfrowaniu) plik nie
# odzyskiwal rozszerzenia/typu, jesli zaszyfrowany plik .helixpro zostal
# przemianowany albo jego nazwa nie byla juz "oryginalna_nazwa.helixpro".

def test_detect_format_plain(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_bytes(b"tresc")
    enc = tmp_path / "dane.helixpro"
    encrypt_file(str(src), str(enc), key=generate_key())
    assert detect_format(str(enc)) == "plain"


def test_detect_format_named(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_bytes(b"tresc")
    enc = tmp_path / "dane.helixpro"
    encrypt_file_with_name(str(src), str(enc), key=generate_key())
    assert detect_format(str(enc)) == "named"


def test_detect_format_unknown_for_random_file(tmp_path):
    junk = tmp_path / "cokolwiek.bin"
    junk.write_bytes(b"nie helix pro")
    assert detect_format(str(junk)) == "unknown"


def test_encrypt_with_name_recovers_original_filename_and_extension(tmp_path):
    """Sedno naprawy: oryginalna nazwa (a wiec i rozszerzenie/typ)
    wraca poprawnie z decrypt_bytes_with_name(), niezaleznie od tego,
    jak jest teraz nazwany plik zaszyfrowany."""
    key = generate_key()
    src = tmp_path / "zdjecie.jpg"
    src.write_bytes(b"\xff\xd8\xff niby-tresc-jpg")
    enc = tmp_path / "cos_zupelnie_innego.bin"  # celowo INNA nazwa niz zrodlo
    encrypt_file_with_name(str(src), str(enc), key=key)

    name, content = decrypt_bytes_with_name(str(enc), key=key)
    assert name == "zdjecie.jpg"
    assert content == src.read_bytes()


def test_decrypt_file_with_name_writes_under_recovered_name(tmp_path):
    key = generate_key()
    src_dir = tmp_path / "zrodlo"
    src_dir.mkdir()
    src = src_dir / "raport.pdf"
    src.write_bytes(b"tresc raportu")
    enc = tmp_path / "przeslany_mailem.dat"  # znowu inna nazwa
    encrypt_file_with_name(str(src), str(enc), key=key)

    out_dir = tmp_path / "odzyskane"
    out_dir.mkdir()
    out_path = decrypt_file_with_name(str(enc), str(out_dir), key=key)

    assert out_path == str(out_dir / "raport.pdf")
    assert open(out_path, "rb").read() == src.read_bytes()


def test_decrypt_bytes_with_name_rejects_plain_format_file(tmp_path):
    """Plik zaszyfrowany starym encrypt_file() (bez nazwy w srodku) nie
    powinien byc po cichu zle zinterpretowany - jasny blad zamiast tego."""
    key = generate_key()
    src = tmp_path / "dane.txt"
    src.write_bytes(b"tresc")
    enc = tmp_path / "dane.helixpro"
    encrypt_file(str(src), str(enc), key=key)  # STARY format, bez nazwy

    with pytest.raises(HelixProError):
        decrypt_bytes_with_name(str(enc), key=key)


def test_decrypt_bytes_with_name_wrong_key_raises(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_bytes(b"tresc")
    enc = tmp_path / "dane.helixpro"
    encrypt_file_with_name(str(src), str(enc), key=generate_key())
    with pytest.raises(HelixProError):
        decrypt_bytes_with_name(str(enc), key=generate_key())


def test_encrypt_with_name_password_mode_roundtrip(tmp_path):
    src = tmp_path / "notatki.md"
    src.write_bytes(b"# tytul\ntresc notatki")
    enc = tmp_path / "wynik.helixpro"
    encrypt_file_with_name(str(src), str(enc), password="haslo-do-testu")

    name, content = decrypt_bytes_with_name(str(enc), password="haslo-do-testu")
    assert name == "notatki.md"
    assert content == src.read_bytes()


def test_encrypt_with_name_preserves_extension_even_with_unicode_filename(tmp_path):
    src = tmp_path / "ważny_plik_żółć.docx"
    src.write_bytes(b"tresc docx")
    enc = tmp_path / "enc.helixpro"
    key = generate_key()
    encrypt_file_with_name(str(src), str(enc), key=key)

    name, content = decrypt_bytes_with_name(str(enc), key=key)
    assert name == "ważny_plik_żółć.docx"
    assert content == src.read_bytes()


def test_encrypt_with_name_compression_shrinks_repetitive_content(tmp_path):
    """Sedno propozycji: gzip 'ten popularny' przed szyfrowaniem -
    zawartosc bardzo powtarzalna (dobry przypadek dla gzip) powinna dac
    mniejszy plik wynikowy niz bez kompresji."""
    key = generate_key()
    src = tmp_path / "powtarzalny.txt"
    src.write_bytes(b"AAAA" * 50_000)  # 200 000 bajtow, bardzo sciśliwe

    enc_compressed = tmp_path / "z_kompresja.helixpro"
    enc_plain = tmp_path / "bez_kompresji.helixpro"
    encrypt_file_with_name(str(src), str(enc_compressed), key=key, compress=True)
    encrypt_file_with_name(str(src), str(enc_plain), key=key, compress=False)

    assert enc_compressed.stat().st_size < enc_plain.stat().st_size

    name, content = decrypt_bytes_with_name(str(enc_compressed), key=key)
    assert name == "powtarzalny.txt"
    assert content == src.read_bytes()


def test_encrypt_with_name_compression_never_inflates_incompressible_content(tmp_path):
    """'Smart' kompresja: dla danych juz nieściśliwych (tu: losowe bajty,
    stoja w miejscu prawdziwych juz-skompresowanych formatow jak jpg/zip)
    plik wynikowy z compress=True nie powinien byc WIEKSZY niz bez proby
    kompresji w ogole - flaga NONE zostaje uzyta zamiast gzip, gdy gzip
    by tylko powiekszyl dane."""
    key = generate_key()
    src = tmp_path / "losowe.bin"
    src.write_bytes(os.urandom(50_000))

    enc_with_attempt = tmp_path / "z_proba.helixpro"
    enc_without_attempt = tmp_path / "bez_proby.helixpro"
    encrypt_file_with_name(str(src), str(enc_with_attempt), key=key, compress=True)
    encrypt_file_with_name(str(src), str(enc_without_attempt), key=key, compress=False)

    # rozne nonce daja rozna dlugosc ciphertextu +0, ale oba powinny byc
    # w tej samej klasie wielkosci - z proba kompresji NIGDY wiekszy
    assert enc_with_attempt.stat().st_size <= enc_without_attempt.stat().st_size

    name, content = decrypt_bytes_with_name(str(enc_with_attempt), key=key)
    assert content == src.read_bytes()


def test_encrypt_with_name_compress_false_roundtrip(tmp_path):
    key = generate_key()
    src = tmp_path / "dane.txt"
    src.write_bytes(b"tresc bez kompresji" * 100)
    enc = tmp_path / "enc.helixpro"
    encrypt_file_with_name(str(src), str(enc), key=key, compress=False)

    name, content = decrypt_bytes_with_name(str(enc), key=key)
    assert name == "dane.txt"
    assert content == src.read_bytes()


def test_decrypt_bytes_with_name_rejects_corrupted_gzip_payload(tmp_path):
    """Jesli flaga mowi 'gzip', ale tresc po odszyfrowaniu nie jest
    poprawnym gzipem (co oznaczaloby uszkodzenie na wczesniejszym etapie,
    niemozliwe przy nietknietym pliku dzieki AES-GCM, ale test sprawdza
    ze blad jest jasny, nie ze rzuca nieoczekiwanym wyjatkiem z gzip)."""
    import gzip as gzip_module
    key = generate_key()

    name_bytes = "plik.txt".encode("utf-8")
    fake_payload = bytes([len(name_bytes)]) + name_bytes + bytes([1]) + b"to nie jest gzip"
    from helix_pro.cipher import encrypt_bytes, MAGIC_NAMED, VERSION, MODE_KEY

    blob = encrypt_bytes(fake_payload, key)
    fake_file = tmp_path / "spreparowany.helixpro"
    fake_file.write_bytes(MAGIC_NAMED + bytes([VERSION]) + MODE_KEY + blob)

    with pytest.raises(HelixProError):
        decrypt_bytes_with_name(str(fake_file), key=key)


def test_encrypt_with_name_rejects_too_long_filename(tmp_path, monkeypatch):
    """300-znakowej nazwy nie da sie utworzyc na prawdziwym systemie
    plikow (limit ok. 255 bajtow na ext4/NTFS - wywalilo by sie wczesniej
    niz nasz kod), wiec podmieniamy os.path.basename() tylko na czas
    tego testu, zeby sprawdzic sam guard w encrypt_file_with_name() bez
    zaleznosci od limitow konkretnego systemu plikow."""
    import helix_pro.cipher as cipher_module

    key = generate_key()
    src = tmp_path / "krotka_nazwa.txt"
    src.write_bytes(b"tresc")
    enc = tmp_path / "enc.helixpro"

    long_name = "a" * 300 + ".txt"
    monkeypatch.setattr(cipher_module.os.path, "basename", lambda p: long_name)

    with pytest.raises(HelixProError):
        encrypt_file_with_name(str(src), str(enc), key=key)
