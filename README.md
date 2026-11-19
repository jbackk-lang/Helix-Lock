# Helix-Lock v0.1.3 Beta

**Szyfrowanie plików AES-256-GCM z opcjonalną kompresją i kontrolą integralności.**

> **Aktualna wersja kodu: v0.1.3 Beta (`main`) — do testów.** Nie jest to niezależnie audytowany produkt do ochrony danych o wysokiej wrażliwości. Pracuj na kopiach plików i zachowaj kopię zapasową.

## Wersja v0.1.3 Beta

Kod v0.1.3 Beta został scalony do gałęzi `main` w PR #4. W tej wersji rozwijany jest regionalny wybór języków (Europa / Ameryka / Azja), lokalne zapamiętywanie ustawienia języka oraz uzupełnianie katalogów tłumaczeń. Poprawiono błąd, przez który kolejne partie tłumaczeń nadpisywały wcześniejsze wpisy słowników.

**Stan weryfikacji:** nie ma potwierdzonego pozytywnego wyniku testów dla scalonej zmiany. **Stan publikacji:** wydanie [v0.1.3 Beta](https://github.com/jbackk-lang/Helix-Lock/releases/tag/v0.1.3) zostało opublikowane; dostępność pakietów instalacyjnych należy sprawdzić w zasobach wydania.

## Pobierz pliki

**[Helix-Lock v0.1.3 Beta — strona wydania](https://github.com/jbackk-lang/Helix-Lock/releases/tag/v0.1.3)**

| System / plik | Pobieranie |
|---|---|
| **Windows x64** — `HelixLock-windows.zip` | [Sprawdź pliki wydania v0.1.3](https://github.com/jbackk-lang/Helix-Lock/releases/tag/v0.1.3) |
| **macOS (Intel)** — `HelixLock-macos.zip` | [Sprawdź pliki wydania v0.1.3](https://github.com/jbackk-lang/Helix-Lock/releases/tag/v0.1.3) |
| **Linux** — `HelixLock-linux.tar.gz` | [Sprawdź pliki wydania v0.1.3](https://github.com/jbackk-lang/Helix-Lock/releases/tag/v0.1.3) |
| **Sumy kontrolne** — `SHA256SUMS.txt` | [Sprawdź pliki wydania v0.1.3](https://github.com/jbackk-lang/Helix-Lock/releases/tag/v0.1.3) |

**Uwaga:** zielony wynik ręcznie uruchomionego workflow potwierdza zakończenie budowania, ale nie gwarantuje, że archiwa zostały dołączone do GitHub Release. Dlatego linki prowadzą do strony wydania, a nie do niepotwierdzonych adresów plików. Jeśli brakuje plików w sekcji **Assets**, nie są jeszcze dostępne do pobrania z wydania.

[Wszystkie wydania](https://github.com/jbackk-lang/Helix-Lock/releases) · [GitHub Actions](https://github.com/jbackk-lang/Helix-Lock/actions/workflows/publish-release.yml)

Pakiety mogą być niepodpisane; Windows może wyświetlić SmartScreen. Przed uruchomieniem sprawdź sumy SHA-256.

## Co potrafi Helix-Lock?

- **Szyfrowanie plików** — AES-256-GCM, klucz 32-bajtowy lub hasło wyprowadzane przez scrypt.
- **Odzyskiwanie nazwy pliku** — oryginalna nazwa i rozszerzenie mogą być zapisane wewnątrz zaszyfrowanej zawartości.
- **Kompresja przed szyfrowaniem** — opcjonalny gzip, stosowany tylko wtedy, gdy zmniejsza dane.
- **Aplikacja graficzna** — obsługa plików, wbudowana Pomoc i przełącznik języka bez konieczności używania terminala.
- **CounterLock** — opcjonalny licznik udanych odczytów związany kryptograficznie z szyfrogramem.
- **AIRP** — prototypy rotacji kluczy, historii integralności, rejestru zdarzeń i punktów kontrolnych.
- **TIMDR-Ω** — eksperymentalne formaty HLOM (predyktory i ograniczona naprawa GF(256)) oraz HLOB (kompresja OBX1 + AES-GCM); nie są domyślnym formatem aplikacji ani audytowanym zamiennikiem szyfrowania.

## Obsługa aplikacji

W głównej aplikacji **Helix-Lock** pole **Hasło** (lub wybór **Plik-klucz**) znajduje się bezpośrednio pod wyborem pliku źródłowego. Język interfejsu zmienia się przełącznikiem **PL / EN** w górnym pasku; program nie łączy dwóch języków w jednej etykiecie. Pomoc jest dostępna przyciskiem **Pomoc / Help** lub klawiszem **F1**. 

Tłumaczenia są obsługiwane przez moduł [`helix_pro/ui_languages.py`](helix_pro/ui_languages.py): angielskie teksty są identyfikatorami, a brakujące tłumaczenia nowych języków mogą korzystać z angielskiego tekstu zastępczego. Dodanie nowego języka wymaga uzupełnienia katalogu tłumaczeń.

## Języki — v0.1.3 Beta

W kodzie v0.1.3 przygotowano wybór języka według regionów **Europa / Ameryka / Azja**. Regiony porządkują listę, ale nie ograniczają wyboru użytkownika. Ustawienie języka jest zapamiętywane lokalnie w `~/.helix_lock/ui-settings.json`.

**Poprawka słowników:** kolejne partie tłumaczeń są dopisywane do istniejących słowników językowych, zamiast nadpisywać wcześniej dodane wpisy. Zmiana została scalona w PR #4 (`7af2483`). **Testy dla tego commita nie zostały potwierdzone** — przed użyciem produkcyjnym zalecane jest uruchomienie `python -m pytest tests/ -q` i sprawdzenie [GitHub Actions](https://github.com/jbackk-lang/Helix-Lock/actions).

**Uwaga:** lista dostępnych języków nie oznacza jeszcze pełnego tłumaczenia. Polski i angielski są językami bazowymi; dla pozostałych brakujące teksty wyświetlane są po angielsku do czasu przygotowania i weryfikacji tłumaczeń. Dotyczy to również komunikatów bezpieczeństwa.

## Co oznaczają przyciski i skróty?

Nie wiesz, czym różni się **HLXP od HLXN**, co oznaczają **AIRP, CounterLock, HLOB/HLOM**, albo jak odczytać komunikaty aplikacji?

Przejdź do **[przewodnika „Co oznacza co?”](docs/README_CO_OZNACZA_CO.md)** — znajdziesz tam opis przycisków, formatów plików, wskaźników bezpieczeństwa oraz instrukcje szyfrowania i odszyfrowywania.

## Uruchomienie z kodu źródłowego

```bash
python -m pip install cryptography pytest
python helix_lock_app.py
```

Pełne testy repozytorium: `python -m pytest tests/ -q`. Ich wynik zależy od środowiska i aktualnej wersji kodu.

## Contributors / Współtwórcy

- **jbackk-lang** — autor i opiekun projektu.
- **ChatGPT (OpenAI)** — wsparcie AI przy przeglądzie kodu, poprawkach interfejsu, dokumentacji i przygotowaniu procesu wydania. Nie jest to konto GitHub ani niezależny autor commitów.

## Dokumentacja i rozwój

- [**Pełna dokumentacja techniczna — README_DETAILS.md**](README_DETAILS.md) — API, przykłady, AIRP, CounterLock, Chronoproces, TIMDR, bezpieczeństwo i ograniczenia.
- [Plan testów wydania](docs/RELEASE_CHECKLIST.md) — budowanie, testy i dystrybucja.
- [**TIMDR-Ω — formaty HLOB i HLOM**](docs/TIMDR_OMEGA_GUIDE.md) — instrukcje, możliwości, testy i ograniczenia.
- [Plan integracji TIMDR](docs/TIMDR_INTEGRATION.md) — architektura i hipotezy.
- [Granice pamięci Chronoprocesu](docs/CHRONOPROCESS_MEMORY_BOUNDARIES.md).
- [Wydania GitHub](https://github.com/jbackk-lang/Helix-Lock/releases) i [wyniki GitHub Actions](https://github.com/jbackk-lang/Helix-Lock/actions).

**Status:** projekt rozwijany eksperymentalnie; AES-256-GCM pochodzi z biblioteki `cryptography`, natomiast integracja Helix-Lock nie przeszła niezależnego audytu bezpieczeństwa.

**Licencja:** MIT — [LICENSE](LICENSE).
