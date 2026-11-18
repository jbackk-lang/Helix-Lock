# Helix-Lock — propozycja informacji do kolejnego wydania beta

> **Status: wersja przygotowywana, NIEOPUBLIKOWANA.** Ten plik nie jest dowodem, że paczki zostały zbudowane, przetestowane lub udostępnione. Numer wersji i tag należy wybrać po zatwierdzeniu zakresu zmian.

## Nowości od poprzedniego wydania beta

- **Pomoc w aplikacji:** przycisk „Pomoc / Co oznacza co?”, okno działające offline, skrót F1, szybki start i przejście do zakładki Pliki.
- **Bezpieczniejszy zapis wyników:** plik tymczasowy w katalogu docelowym i zastąpienie wyniku dopiero po udanej operacji; ochrona przed zapisaniem wyniku na pliku źródłowym.
- **Czytelniejsze komunikaty:** pełna ścieżka pliku wynikowego, potwierdzenie nadpisania z nazwą pliku i wskazówki przy błędach.
- **Rozpoznawanie nagłówków:** identyfikacja obsługiwanych formatów w panelu informacyjnym.
- **Dokumentacja:** polski przewodnik [Co oznacza co?](README_CO_OZNACZA_CO.md).

## Co należy sprawdzić przed publikacją

1. Wybierz numer kolejnej wersji beta i zatwierdź commit do wydania.
2. Potwierdź, że kompilacje Windows, macOS Intel i Linux dla **tego samego commita** zakończyły się pomyślnie.
3. Uruchom program na rzeczywistych systemach i sprawdź szyfrowanie/odszyfrowywanie, klucz i hasło, Pomoc/F1 oraz nadpisywanie.
4. Utwórz tag `v...` wskazujący zatwierdzony commit. To uruchamia `.github/workflows/publish-release.yml`.
5. Sprawdź wynik zadania publikacji i obecność archiwów `HelixLock-windows.zip`, `HelixLock-macos.zip`, `HelixLock-linux.tar.gz` oraz `SHA256SUMS.txt`.
6. Pobierz archiwa i zweryfikuj sumy SHA-256; dopiero wtedy zaktualizuj linki w głównym README.

## Ograniczenia bezpieczeństwa

Projekt jest w fazie beta i nie przeszedł niezależnego audytu. Przechowuj kopie plików oraz kluczy. AIRP, CounterLock i formaty HLOB/HLOM zawierają funkcje eksperymentalne; wykrycie formatu nie potwierdza autentyczności pliku. Paczki mogą być niepodpisane, a udany build nie zastępuje testów uruchomieniowych.

## Publikacja przez GitHub

W repozytorium otwórz **Releases → Draft a new release**, a następnie utwórz nowy tag `v...` z zatwierdzonego commita. **Uwaga:** sam ręcznie utworzony szkic wydania nie uruchomi workflow; wyzwalaczem jest wypchnięcie nowego tagu `v*` do repozytorium. Najbezpieczniej utworzyć tag i wypchnąć go przez Git, poczekać na workflow, a następnie sprawdzić opublikowane pliki.
