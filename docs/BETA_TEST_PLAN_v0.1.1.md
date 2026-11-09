# Helix-Lock v0.1.1 — plan niezależnych testów beta

## Cel

Uzupełnić testy automatyczne i testy właściciela o niezależne testy użytkowników na rzeczywistych komputerach. Beta ma wykrywać problemy kompatybilności, ergonomii, instalacji i błędy aplikacyjne, zanim projekt zostanie szerzej udostępniony.

Beta nie jest audytem kryptograficznym i nie może być przedstawiana jako dowód bezpieczeństwa.

## Model testowania

### Poziom 1 — testy automatyczne projektu

- Testy regresyjne i macierz wspieranych wersji Pythona.
- Budowanie paczek Windows, macOS i Linux.
- Testy formatu, błędnych kluczy, zmodyfikowanych szyfrogramów, błędów zapisu i aliasów ścieżek.
- Każda poprawka błędu otrzymuje test regresyjny, jeśli da się go odtworzyć automatycznie.

### Poziom 2 — testy właściciela

Właściciel sprawdza na własnych urządzeniach:
- instalację, uruchomienie, aktualizację i odinstalowanie;
- szyfrowanie i odszyfrowanie reprezentatywnych plików;
- zgodność SHA-256 pliku wejściowego i odzyskanego;
- plik-klucz i hasło, błędne dane uwierzytelniające;
- zachowanie aplikacji przy anulowaniu, braku miejsca i błędach dostępu;
- czytelność interfejsu, skalowanie i długie ścieżki.

### Poziom 3 — niezależna beta zamknięta

Zaprosić niewielką, zróżnicowaną grupę testerów:
- różne wersje Windows, macOS i dystrybucje Linux;
- standardowe konta bez uprawnień administratora;
- różne systemy plików, dyski i poziomy wolnego miejsca;
- różne rozmiary i typy plików;
- różne rozdzielczości i skalowania ekranu.

Na początku udostępniać tylko stabilną ścieżkę szyfrowania. HNS1, eksperymentalny odbiornik Replay i inne prototypy nie mogą być domyślnie aktywowane ani przedstawiane jako funkcje produkcyjne.

## Bezpieczeństwo uczestników

- Testerzy otrzymują jasne ostrzeżenie: beta nie jest przeznaczona do jedynych kopii ważnych danych.
- Używać wyłącznie kopii danych testowych, nigdy jedynego egzemplarza dokumentu.
- Przed testami wykonać kopię zapasową danych.
- Nie wysyłać zespołowi kluczy, haseł, plaintextu ani prawdziwych plików użytkownika.
- Raport błędu powinien zawierać wersję aplikacji, system operacyjny, kroki reprodukcji, oczekiwany i rzeczywisty wynik oraz — jeśli możliwe — log po sprawdzeniu, że nie zawiera sekretów.
- Nie prosić testerów o wyłączenie Defendera, Gatekeepera ani innych zabezpieczeń systemu.
- Nie publikować automatycznie plików zrzutu pamięci, które mogą zawierać dane wrażliwe.

## Raportowanie błędów i prywatność

Preferowany jest jawny, dobrowolny raport błędu przez wskazany kanał projektu.

Jeśli w przyszłości zostanie dodana telemetria:
- musi być opt-in i wyłączona domyślnie;
- musi być opisana przed wysłaniem;
- nie może wysyłać treści plików, kluczy, haseł, nonce ani odszyfrowanych danych;
- powinna ograniczać dane do wersji aplikacji, systemu, kategorii błędu i minimalnego kontekstu diagnostycznego;
- tester musi móc zgłosić błąd bez telemetryki.

Nie dodawać ukrytego śledzenia aktywności ani automatycznego uploadu logów.

## Priorytety zgłoszeń

- **P0 — krytyczny:** możliwość odzyskania cudzych danych, ujawnienie plaintextu/klucza, błędna akceptacja zmodyfikowanego szyfrogramu, utrata lub cicha korupcja danych. Natychmiast wstrzymać dystrybucję beta i wydać poprawkę po analizie.
- **P1 — wysoki:** utrata danych w typowym scenariuszu, awaria deszyfrowania, błędne zarządzanie kluczem, powtarzalny crash. Wstrzymać kolejne rozszerzanie beta.
- **P2 — normalny:** problem kompatybilności, instalacji lub interfejsu z obejściem.
- **P3 — niski:** kosmetyka i sugestie użyteczności.

Każde zgłoszenie musi zostać odtworzone, sklasyfikowane i zamknięte testem regresyjnym albo uzasadnioną decyzją.

## Warunki przejścia z beta do wydania

- Brak otwartych P0 i P1.
- Testy automatyczne zielone dla zatwierdzonego commitu.
- Przejście testów właściciela na wspieranych systemach.
- Zebrane wyniki niezależnej bety, w tym liczba testerów, systemy i odtworzone błędy.
- Sprawdzone paczki, manifest SHA-256 i instrukcja bezpiecznej aktualizacji.
- Jawnie opublikowane ograniczenia i znane problemy.
- Niezależny przegląd bezpieczeństwa przed deklaracjami o odporności na ataki lub certyfikacji.

Sama liczba testerów ani brak zgłoszeń nie dowodzą braku błędów.

## Wydanie etapami

1. Wewnętrzne testy i testy właściciela.
2. Zamknięta beta dla zaproszonych testerów.
3. Poprawki i ponowne testy regresyjne.
4. Opcjonalna szersza beta po ocenie ryzyka.
5. Wydanie stabilne dopiero po spełnieniu bramek wydania.

## Status

Dokument opisuje plan. Nie oznacza, że beta została już uruchomiona ani że testerzy zostali zrekrutowani.

## Przygotowane elementy repozytorium — 2026-11-09

- Publiczny formularz GitHub Issues wymaga wersji/commitu, systemu, obszaru,
  kroków reprodukcji, oczekiwanego i rzeczywistego wyniku oraz potwierdzenia,
  że tester użył kopii i nie dołączył sekretów.
- Formularz publiczny wyraźnie kieruje podejrzenia podatności do prywatnego
  kanału; nie zawiera publicznej kategorii P0.
- Dodano `SECURITY.md` z zasadami odpowiedzialnego ujawniania podatności.
  Prywatne zgłoszenia GitHub należy włączyć i sprawdzić przed zaproszeniem
  testerów; sam link nie dowodzi, że funkcja jest aktywna.
- Workflow budowania desktopu publikuje osobny `SHA256SUMS.txt` wraz z
  paczką i metadanymi środowiska dla każdej platformy.
- Walidacja workflow [42548449037](https://github.com/jbackk-lang/Helix-Lock/actions/runs/42548449037)
  zakończyła się sukcesem na Windows, macOS i Linux, łącznie z generowaniem
  i dołączeniem manifestów SHA-256. To walidacja pakowania, nie test
  uruchomienia aplikacji na fizycznych komputerach.
- Z repo usunięto śledzone pliki `__pycache__/*.pyc` i dodano `.gitignore`.

Zewnętrzna beta nadal nie została uruchomiona. Przed naborem należy sprawdzić
ustawienia prywatnego raportowania podatności, pobrać artefakty, niezależnie
zweryfikować ich SHA-256 i przeprowadzić test instalacji/uruchomienia.
