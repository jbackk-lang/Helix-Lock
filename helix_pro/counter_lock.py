"""
helix_pro/counter_lock.py — naprawiona wersja pomyslu z HLX1.py (licznik
odczytow / ochrona przed cofnieciem starszej kopii pliku).

Co bylo zle w HLX1.py: payload byl tylko `base64.b64encode(data)` -
zadnego szyfrowania. Podpis HMAC-SHA256 chronil naglowek+payload przed
manipulacja (to bylo zrobione poprawnie: stale-czasowe porownanie), ale
skoro payload i tak byl jawny po zdekodowaniu base64, sam pomysl
"zabezpiecz plik" byl fikcja - kazdy z dostepem do pliku czytal tresc
bez klucza.

Jak to jest naprawione tutaj: dane sa faktycznie szyfrowane AES-256-GCM
(patrz cipher.py), a licznik jest wpiety jako AAD (additional
authenticated data) w te sama operacje AES-GCM, zamiast osobnego
podpisu HMAC nad base64. Efekt: nie da sie ani odczytac tresci bez
klucza, ani podmienic/cofnac licznika bez uniewaznienia calego tagu
uwierzytelniajacego (probe odszyfrowania z innym licznikiem w AAD
zawsze konczy sie HelixProError).
"""
from __future__ import annotations

import struct

from .cipher import encrypt_bytes, decrypt_bytes, HelixProError

MAGIC = b"HLXC"
VERSION = 1
COUNTER_STRUCT = ">Q"  # 8-bajtowy licznik bez znaku, big-endian
COUNTER_SIZE = struct.calcsize(COUNTER_STRUCT)


class CounterLock:
    """Opakowuje dane z rosnacym licznikiem, kryptograficznie zwiazanym
    z ciphertextem. Uzycie:

        lock = CounterLock(key)
        blob = lock.lock(b"tajna tresc", counter=0)
        data, counter = lock.unlock(blob)                    # odczyt
        data, counter, next_blob = lock.unlock_and_advance(blob)  # odczyt + inkrementacja
    """

    def __init__(self, key: bytes):
        self._key = key

    def lock(self, data: bytes, counter: int) -> bytes:
        if counter < 0:
            raise HelixProError("licznik nie moze byc ujemny")
        counter_bytes = struct.pack(COUNTER_STRUCT, counter)
        blob = encrypt_bytes(data, self._key, aad=counter_bytes)
        return MAGIC + bytes([VERSION]) + counter_bytes + blob

    def unlock(self, blob: bytes) -> tuple[bytes, int]:
        if blob[:4] != MAGIC:
            raise HelixProError("nieznany format (brak naglowka CounterLock)")
        version = blob[4]
        if version != VERSION:
            raise HelixProError(f"nieobslugiwana wersja CounterLock: {version}")
        offset = 5
        counter_bytes = blob[offset:offset + COUNTER_SIZE]
        (counter,) = struct.unpack(COUNTER_STRUCT, counter_bytes)
        ciphertext_part = blob[offset + COUNTER_SIZE:]
        # counter_bytes musi byc podane jako AAD identyczne z tym uzytym
        # przy lock() - jesli ktos podmienil licznik w naglowku, AAD sie
        # nie zgodzi z tym wpieta przy szyfrowaniu i decrypt_bytes rzuci.
        data = decrypt_bytes(ciphertext_part, self._key, aad=counter_bytes)
        return data, counter

    def unlock_and_advance(self, blob: bytes) -> tuple[bytes, int, bytes]:
        data, counter = self.unlock(blob)
        next_blob = self.lock(data, counter + 1)
        return data, counter, next_blob
