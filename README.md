# Helix-Lock

**Szyfrowanie plików AES-256-GCM z opcjonalną kompresją i kontrolą integralności.**

> **v0.1.1 BETA — do testów.** Nie jest to niezależnie audytowany produkt do ochrony danych o wysokiej wrażliwości. Pracuj na kopiach plików i zachowaj kopię zapasową.

## Pobierz pliki

| System / plik | Pobieranie |
|---|---|
| **Windows x64** — `HelixLock-windows.zip` | [Pobierz ZIP](https://github.com/jbackk-lang/Helix-Lock/releases/download/v0.1.1-beta.2/HelixLock-windows.zip) |
| **macOS** — `HelixLock-macos.zip` | [Pobierz ZIP](https://github.com/jbackk-lang/Helix-Lock/releases/download/v0.1.1-beta.2/HelixLock-macos.zip) |
| **Linux** — `HelixLock-linux.tar.gz` | [Pobierz TAR.GZ](https://github.com/jbackk-lang/Helix-Lock/releases/download/v0.1.1-beta.2/HelixLock-linux.tar.gz) |
| **Sumy kontrolne** — `SHA256SUMS-builds.txt` | [Pobierz SHA-256](https://github.com/jbackk-lang/Helix-Lock/releases/download/v0.1.1-beta.2/SHA256SUMS-builds.txt) |

[**Wszystkie wydania i informacje o wersji beta**](https://github.com/jbackk-lang/Helix-Lock/releases)

Pakiety mogą być niepodpisane; Windows może wyświetlić SmartScreen. Przed uruchomieniem sprawdź sumy SHA-256. Aktualne kompilacje CI nie muszą być identyczne z plikami opublikowanego wydania.

## Co potrafi Helix-Lock?

- **Szyfrowanie plików** — AES-256-GCM, klucz 32-bajtowy lub hasło wyprowadzane przez scrypt.
- **Odzyskiwanie nazwy pliku** — oryginalna nazwa i rozszerzenie mogą być zapisane wewnątrz zaszyfrowanej zawartości.
- **Kompresja przed szyfrowaniem** — opcjonalny gzip, stosowany tylko wtedy, gdy zmniejsza dane.
- **Aplikacja graficzna** — obsługa plików i kolejki operacji bez konieczności używania terminala.
- **CounterLock** — opcjonalny licznik udanych odczytów związany kryptograficznie z szyfrogramem.
- **AIRP** — prototypy rotacji kluczy, historii integralności, rejestru zdarzeń i punktów kontrolnych.
- **TIMDR-Ω** — eksperymentalne formaty HLOM (predyktory i ograniczona naprawa GF(256)) oraz HLOB (kompresja OBX1 + AES-GCM); nie są domyślnym formatem aplikacji ani audytowanym zamiennikiem szyfrowania.

## Uruchomienie z kodu źródłowego

```bash
python -m pip install cryptography pytest
python helix_pro_gui.py
```

Pełne testy repozytorium: `python -m pytest tests/ -q`. Ich wynik zależy od środowiska i aktualnej wersji kodu.

## Dokumentacja i rozwój

- [**Pełna dokumentacja techniczna — README_DETAILS.md**](README_DETAILS.md) — API, przykłady, AIRP, CounterLock, Chronoproces, TIMDR, bezpieczeństwo i ograniczenia.
- [Plan testów wydania](docs/RELEASE_CHECKLIST.md) — budowanie, testy i dystrybucja.
- [**TIMDR-Ω — formaty HLOB i HLOM**](docs/TIMDR_OMEGA_GUIDE.md) — instrukcje, możliwości, testy i ograniczenia.
- [Plan integracji TIMDR](docs/TIMDR_INTEGRATION.md) — architektura i hipotezy.
- [Granice pamięci Chronoprocesu](docs/CHRONOPROCESS_MEMORY_BOUNDARIES.md).
- [Wydania GitHub](https://github.com/jbackk-lang/Helix-Lock/releases) i [wyniki GitHub Actions](https://github.com/jbackk-lang/Helix-Lock/actions).

**Status:** projekt rozwijany eksperymentalnie; AES-256-GCM pochodzi z biblioteki `cryptography`, natomiast integracja Helix-Lock nie przeszła niezależnego audytu bezpieczeństwa.

**Licencja:** MIT — [LICENSE](LICENSE).
