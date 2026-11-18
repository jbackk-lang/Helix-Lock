# TIMDR-Ω — przewodnik po eksperymentalnych formatach

> **Status: eksperymentalny, opt-in.** To nie jest domyślny format aplikacji ani niezależnie audytowany produkt kryptograficzny. Nie testuj na jedynej kopii danych.

## Wybór formatu

| Format | Moduł | Co zapewnia | Czego nie zapewnia |
|---|---|---|---|
| **HLXP / HLXN** | `helix_pro/cipher.py` | Domyślne AES-256-GCM; HLXN może zachować oryginalną nazwę pliku | Naprawy uszkodzonych bloków |
| **HLOM** | `helix_pro/timdr_archive_cipher.py` | AES-GCM, predyktory HTO4, archiwum HTO3/HTO2 i ograniczona nadmiarowość GF(256) | Nieograniczonej naprawy; gwarancji lepszej kompresji |
| **HLOB** | `helix_pro/timdr_obx_cipher.py` | OBX1 przed AES-256-GCM, uwierzytelniony nagłówek, atomowy zapis wyniku | Naprawy GF(256), strumieniowania, integracji z GUI |

OBX1 (`experiments/omega_block_codec.py`) jest **odwracalnym kodekiem kompresji**, nie szyfrem. Poufność HLOB i HLOM pochodzi z AES-GCM, nie z transformacji predykcyjnych.

## Przykład: HLOB

Uruchom z katalogu głównego repozytorium po zainstalowaniu `cryptography`.

```python
from helix_pro.cipher import generate_key
from helix_pro.timdr_obx_cipher import encrypt_file_obx, decrypt_file_obx

key = generate_key()  # przechowuj poza zaszyfrowanymi danymi
encrypt_file_obx("wejscie.bin", "archiwum.hlob", key=key)
decrypt_file_obx("archiwum.hlob", "odtworzone.bin", key=key)
```

Zamiast `key=key` można użyć `password="silne-haslo"` w obu wywołaniach. Nie podawaj obu metod jednocześnie. HLOB wymaga osobnych ścieżek wejścia i wyjścia; przy błędnym uwierzytelnieniu nie zapisuje plaintextu. Przed zapisem pliku docelowego używa pliku tymczasowego i `os.replace`, więc **może zastąpić istniejący plik docelowy po poprawnym odszyfrowaniu**.

HLOB wczytuje całą zawartość do pamięci. Domyślny limit wejścia i odtworzonego wyniku to **256 MiB**. To nie jest limit całkowitego użycia RAM.

## Przykład: HLOM

```python
from helix_pro.cipher import generate_key
from helix_pro.timdr_archive_cipher import encrypt_file_omega, decrypt_file_omega

key = generate_key()
encrypt_file_omega("wejscie.bin", "archiwum.hlom", key=key, predictor="fast")
repaired_blocks = decrypt_file_omega("archiwum.hlom", "odtworzone.bin", key=key)
print("Naprawione bloki:", repaired_blocks)
```

HLOM obsługuje także hasło. Predyktor `fast` wybiera tryb na podstawie próbki 8 KiB; dostępne są też `raw`, `1d`, `2d`, `3d` i `auto`. Liczba naprawionych bloków nie oznacza gwarancji odzyskania dowolnie uszkodzonego archiwum. Obecna implementacja HLOM zapisuje wynik bez atomowej podmiany; nie traktuj jej jako bezpiecznego narzędzia do nadpisywania ważnych plików.

## Testy

```bash
python -m pip install cryptography pytest
python -m pytest -q tests/test_omega_block_codec.py tests/test_omega_block_codec_hardening.py tests/test_timdr_obx_cipher.py tests/test_timdr_archive_cipher.py tests/test_compare_hlob_hlom.py
```

Powyższe polecenie jest instrukcją, **nie deklaracją, że testy zostały tutaj uruchomione**. Status CI sprawdzaj w [GitHub Actions](https://github.com/jbackk-lang/Helix-Lock/actions).

## Porównanie HLOB i HLOM

```bash
python -m benchmarks.compare_hlob_hlom sciezka/do/pliku.bin --repeats 3 --output wyniki.json
```

Benchmark zapisuje rozmiary archiwów, mediany czasów szyfrowania i odszyfrowania, próbki czasowe oraz kontrolę zgodności SHA-256 odtworzonych danych. Uruchamia oba formaty na tym samym wejściu i kluczu.

**Interpretacja:** HLOM zawiera bloki nadmiarowe GF(256), HLOB nie — nie są funkcjonalnie równoważne. Benchmark nie wykonuje rozgrzewki, profilowania pamięci ani testów uszkodzeń. Nie porównuj wyników z 7-Zip/RAR bez uzgodnienia ustawień szyfrowania, kompresji i naprawy.

## Zasady bezpieczeństwa i zgodności

- Nie zmieniaj domyślnego HLXP/HLXN na format eksperymentalny bez świadomej decyzji użytkownika.
- Zachowuj kopie źródłowe i klucze poza katalogiem wynikowym.
- Uwierzytelnienie AES-GCM nie zastępuje kopii zapasowej ani nie zapewnia odzyskiwania po utracie klucza.
- Przed wykorzystaniem do ważnych danych potrzebne są testy awaryjne, testy na docelowych platformach i niezależny audyt.

Dalsze informacje: [pełna dokumentacja projektu](../README_DETAILS.md), [integracja TIMDR](TIMDR_INTEGRATION.md).
