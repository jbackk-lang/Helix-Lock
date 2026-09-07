"""
helix_pro — ulepszona ("Pro") wersja Helix-Lock, naprawiajaca konkretne
problemy znalezione w audycie oryginalnych modulow tego repo:

1. HLX1.py (licznik odczytow) W OGOLE NIE SZYFROWAL payloadu - uzywal
   `base64.b64encode(data)`, co jest kodowaniem, nie szyfrowaniem. Kazdy
   z dostepem do pliku odczytal tresc bez znajomosci klucza. Jedyna
   realna ochrona to podpis HMAC-SHA256 nad naglowkiem+payloadem (i to
   zrobione poprawnie - stale-czasowe porownanie `hmac.compare_digest`),
   ale to chronilo licznik przed manipulacja, nie tresc przed odczytem.
2. helix_cipher.py uzywal klucza = goly `SHA256(haslo)` bez soli i bez
   stretchingu (KDF) - podatne na brute-force/slownikowy atak offline
   przy niezbyt losowym hasle. Do tego AES-CBC bez zadnej autentykacji -
   podatne na modyfikacje ciphertextu bez wykrycia (padding oracle /
   bit-flipping).
3. helix_lock_cipher.py byl juz solidny (prawdziwe AES-256-GCM z
   audytowanej biblioteki `cryptography`), ale obslugiwal tylko tryb
   pliku-klucza, nie hasla, i nie mial nic do ochrony przed odtwarzaniem
   (replay) starszej wersji zaszyfrowanego pliku.

helix_pro laczy oba tryby (plik-klucz ORAZ haslo+scrypt) w jednym API
opartym w calosci na AES-256-GCM, plus counter_lock.py - naprawiona
wersja pomyslu z HLX1, gdzie licznik jest kryptograficznie zwiazany z
ciphertextem (AAD w AES-GCM), a nie tylko podpisany obok jawnego base64.

Patrz helix_pro/cipher.py i helix_pro/counter_lock.py po szczegoly, oraz
README.md sekcja "Helix Pro - co naprawiono".
"""
from .cipher import (
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
from .counter_lock import (
    CounterLock,
    encrypt_file_with_counter,
    decrypt_file_with_counter,
)

__all__ = [
    "generate_key",
    "derive_key_from_password",
    "encrypt_bytes",
    "decrypt_bytes",
    "encrypt_file",
    "decrypt_file",
    "encrypt_file_with_name",
    "decrypt_bytes_with_name",
    "decrypt_file_with_name",
    "detect_format",
    "HelixProError",
    "CounterLock",
    "encrypt_file_with_counter",
    "decrypt_file_with_counter",
]
