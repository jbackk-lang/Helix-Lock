# Helix-Lock — co oznacza co? Przewodnik użytkownika

Ten dokument wyjaśnia nazwy, przyciski i komunikaty w aplikacji. Dotyczy przede wszystkim głównej aplikacji desktopowej `helix_lock_app.py`; pomocniczy `helix_pro_gui.py` ma nieco inny układ i dodatkowe opcje.

> **Ważne:** projekt jest w fazie beta. Zawsze zachowuj kopię oryginału i kopię klucza. Rozpoznanie formatu pliku lub zielony status kompilacji nie stanowią dowodu bezpieczeństwa.

## Podstawowe czynności

| Element | Znaczenie | Co zrobić |
|---|---|---|
| **Plik źródłowy / Source file** | Plik, który chcesz zaszyfrować albo odszyfrować | Wskaż istniejący plik |
| **Plik-klucz / Key file** | Plik zawierający dokładnie 32 bajty tajnego klucza | Przechowuj osobno od zaszyfrowanych danych; nie wysyłaj go nikomu |
| **Hasło / Password** | Alternatywa dla pliku-klucza; program wyprowadza klucz za pomocą scrypt | Użyj mocnego hasła; jego utrata uniemożliwi odzyskanie danych |
| **Wygeneruj nowy klucz** | Tworzy losowy klucz do przyszłego szyfrowania | Zrób bezpieczną kopię i nie nadpisuj istniejącego klucza |
| **Szyfruj / Encrypt** | Tworzy zaszyfrowaną kopię wybranego pliku | Wybierz nazwę i miejsce zapisu |
| **Odszyfruj / Decrypt** | Odtwarza dane po poprawnej weryfikacji kryptograficznej | Podaj właściwy klucz albo hasło |
| **Zapisz jako / Save as** | Wybór miejsca i nazwy wyniku | Nie wskazuj pliku źródłowego |
| **Nadpisanie / Overwrite** | Plik docelowy już istnieje | Potwierdź tylko, gdy świadomie chcesz go zastąpić |
| **Status** | Informacja o operacji lub błędzie | Nie traktuj samej etykiety formatu jako potwierdzenia autentyczności |

W głównej aplikacji wyniki szyfrowania i odszyfrowywania są przygotowywane w pliku tymczasowym, a następnie przenoszone na wskazaną ścieżkę po pomyślnym zakończeniu operacji. Potwierdzenie nadpisania nadal oznacza zgodę na zastąpienie istniejącego pliku.

## Jak zaszyfrować plik?

1. Otwórz Helix-Lock i wybierz **Plik źródłowy**.
2. Wybierz **Plik-klucz** albo **Hasło**; jeśli nie masz klucza, użyj **Wygeneruj nowy klucz** i zachowaj jego kopię.
3. Kliknij **Szyfruj**, wskaż miejsce zapisu i sprawdź komunikat końcowy.
4. Zachowaj oryginalny plik, dopóki nie upewnisz się, że potrafisz odszyfrować kopię.

## Jak odszyfrować plik?

1. Wybierz zaszyfrowany plik jako źródło.
2. Wskaż **ten sam klucz** albo wpisz **to samo hasło**, które służyło do szyfrowania.
3. Kliknij **Odszyfruj** i wybierz miejsce zapisu.
4. Sprawdź zawartość odzyskanego pliku przed usunięciem jakichkolwiek kopii.

W głównej aplikacji format **CounterLock** nie jest odszyfrowywany zwykłym przyciskiem: wymaga osobnej kontroli licznika i rejestru. Eksperymentalne **HLOB/HLOM** są rozpoznawane w panelu informacji, ale nie są automatycznie obsługiwane przez standardowy przycisk odszyfrowywania.

## Format pliku — co oznaczają skróty?

| Nazwa | Co oznacza | Ważne ograniczenie |
|---|---|---|
| **HLXP** | Podstawowy format zaszyfrowanego pliku Helix Pro | Nie zapewnia sam z siebie naprawy uszkodzonych danych |
| **HLXN** | Format z oryginalną nazwą pliku zapisaną wewnątrz zaszyfrowanej zawartości | Nazwa jest odzyskiwana dopiero po odszyfrowaniu |
| **HLXC / CounterLock** | Format z licznikiem odczytów powiązanym kryptograficznie z zawartością | Sam licznik nie zastępuje niezależnego, trwałego rejestru |
| **HLOB** | Eksperymentalny format: kompresja OBX1 + AES-256-GCM | Bez naprawy GF(256), bez strumieniowania; nie jest standardowym trybem GUI |
| **HLOM** | Eksperymentalny format Omega: predyktory i ograniczona naprawa GF(256) + szyfrowanie | Większy narzut; naprawa nie jest gwarantowana dla dowolnego uszkodzenia |
| **OBX1** | Odwracalny kodek kompresji używany przez HLOB | Sam OBX1 **nie szyfruje** danych |

Jeżeli panel pokazuje **„Unknown / plain file”**, oznacza to tylko, że nagłówek nie pasuje do rozpoznawanych formatów. Nie oznacza automatycznie, że plik jest bezpieczny, nieszyfrowany lub nieuszkodzony.

## Panel bezpieczeństwa — co pokazują wskaźniki?

| Wskaźnik | Znaczenie |
|---|---|
| **AIRP Chain / Łańcuch AIRP** | Lokalna kontrola spójności kolejnych wpisów dziennika |
| **Sequence / Sekwencja** | Liczba wpisów w lokalnym dzienniku |
| **Checkpoint** | Informacja o punkcie kontrolnym; brak weryfikacji zewnętrznej nie oznacza sukcesu |
| **CounterLock counter / Licznik** | Licznik zapisany w nagłówku lub rejestrze; odczyt nagłówka jest **niezweryfikowany** |
| **File format / Format pliku** | Rozpoznanie nagłówka, a nie weryfikacja hasła czy integralności |
| **Events / Zdarzenia** | Liczba zdarzeń zapisanych w lokalnym dzienniku |
| **Event timeline / Oś zdarzeń** | Ostatnie zdarzenia AIRP, bez treści szyfrowanych plików |

**AIRP** to rozwijany system rejestrowania tożsamości kluczy, zdarzeń i integralności. **Trust Anchor** oznacza zewnętrzny punkt zaufania, a **quorum** — wymaganą większość niezależnych świadków. Sama lokalna baza SQLite nie chroni przed cofnięciem całej bazy do wcześniejszego stanu.

## Odciski kluczy i plików

- **Key fingerprint / Odcisk klucza:** identyfikator pozwalający porównać tożsamość klucza; **nie jest samym kluczem** i nie odszyfruje pliku.
- **Ciphertext fingerprint / Odcisk szyfrogramu:** wartość kontrolna wyliczana dla zaszyfrowanego pliku, pomocna przy porównaniu reprezentacji.
- **Manifest:** plik z informacjami o identyfikatorach i odcisku; nie powinien zawierać tajnego klucza ani hasła.
- **Object ID / ID obiektu:** nazwa identyfikująca obiekt w rejestrze.
- **Key ID / ID klucza:** identyfikator wersji/tożsamości klucza w rejestrze, nie tajny materiał klucza.
- **Rotate key / Rotuj klucz:** procedura zmiany powiązania klucza w AIRP; nie należy jej utożsamiać z automatycznym odszyfrowaniem wszystkich plików.

## Najczęstsze komunikaty

| Komunikat | Co oznacza / co zrobić |
|---|---|
| **Nie rozpoznano formatu** | Wskazany plik nie pasuje do standardowych formatów obsługiwanych przez operację odszyfrowywania |
| **Niepoprawny klucz / hasło albo błąd uwierzytelnienia** | Sprawdź klucz, hasło i to, czy szyfrogram nie został zmodyfikowany |
| **Plik istnieje. Nadpisać?** | Wynik zastąpi wskazany plik; anuluj, jeśli nie masz kopii |
| **Brak bazy AIRP / No database** | Brak lokalnego rejestru; to nie jest pozytywna weryfikacja |
| **Chain OK** | Lokalny łańcuch wpisów jest spójny według kontroli aplikacji; nie dowodzi niezależnego zakotwiczenia |
| **Not checked / Nie sprawdzono** | Zewnętrzna weryfikacja nie została przeprowadzona |

## Gdzie szukać szczegółów?

- [README główne](../README.md) — pobieranie programu i krótki opis możliwości
- [README_DETAILS.md](../README_DETAILS.md) — szczegóły techniczne, API i ograniczenia
- [TIMDR-Ω — HLOB/HLOM](TIMDR_OMEGA_GUIDE.md) — eksperymentalne formaty i ich ograniczenia
- [Lista kontrolna wydania](RELEASE_CHECKLIST.md) — wymagane kontrole przed publikacją

**Status:** dokument opisuje bieżący kod repozytorium. Starsze pakiety pobrane z GitHub Releases mogą mieć inne ekrany i nie zawierać najnowszych zmian.
