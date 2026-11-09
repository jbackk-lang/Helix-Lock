# Helix-Lock — zamknięcie etapu i zapis na przyszłość
Data: 2026-11-08

## Decyzja właściciela
Zatrzymać rozbudowę i eksperymenty. Zachować istniejący kod i wyniki.
Do dalszych prac wrócić kiedyś, bez ponownego rozpoczynania dyskusji od zera.
Priorytet: prostota, bezpieczeństwo, działający program. Nie obiecywać
przełomu ani przewagi bez dowodów.

## Co istnieje
- Zalecana aplikacja desktopowa i API: `helix_pro/`, `helix_pro_gui.py`.
  Obsługa plików, AES-256-GCM, hasło przez scrypt, nazwa pliku i opcjonalna
  kompresja. To jest istniejąca ścieżka użytkowa.
- Wcześniej zweryfikowane budowanie paczek na Windows/macOS/Linux:
  GitHub Actions 42502363536; nie jest to dowód działania GUI na sprzęcie.
- Na gałęzi `experiment/helix-native`: eksperymentalne formaty HNA1
  (uwierzytelniony plik) i HNS1 (uwierzytelniony strumień po 64 KiB);
  testy integralności, ucięcia, złego klucza, atomowej podmiany pliku,
  pamięci i awarii procesu. Ostatnie potwierdzone CI:
  https://github.com/jbackk-lang/Helix-Lock/actions/runs/42515042169
  (commit 229a273bf70480eff268c33963d6a475239714f7).
- Kodowanie fazowe QPSK, powtórzone obserwacje, rezonans, współfaza,
  konsensus i syntetyczne odbicia. Nie stanowią szyfru ani funkcji
  produkcyjnego GUI. Test pokazuje, że skorelowane echo może oszukać
  jednogłośny konsensus.
- Odbiornik replay i eksperymentalna obsługa jego stanu są WYŁĄCZONE
  z zakresu wydania. Nie wznawiać tego wątku bez nowej decyzji właściciela.

## Czego nie ukończono — stan faktyczny
- Brak potwierdzonego wydania/tagu końcowego zawierającego nowe eksperymenty;
  nie utożsamiać zielonego CI z publicznym wydaniem.
- HNS1/HNA1 nie są zintegrowane z zalecaną aplikacją desktopową jako
  wspierany format; zachować je osobno, aby nie zepsuć zgodności.
- Brak ręcznych testów GUI na rzeczywistych Windows, macOS i Linux.
- Brak niezależnego audytu bezpieczeństwa i testów utraty zasilania
  (w tym trwałości metadanych katalogu).
- Brak ukończonego podpisywania/notaryzacji paczek i potwierdzonego
  procesu dystrybucji na wszystkich platformach.
- Brak pomiarów na rzeczywistym kanale dla mechanizmów fazowych oraz
  obiektywnie ustalonych progów korzyści względem prostego dekodera.
- Nie potwierdzono kompletnego przeglądu zależności, kompatybilności
  formatów i cyklu życia kluczy dla nowej ścieżki HNS1.

## Możliwości przypuszczalne, NIE potwierdzone
- HNS1 może pozwolić na obsługę bardzo dużych plików przy ograniczonym
  użyciu pamięci; test 12 MiB nie dowodzi zachowania przy dowolnym rozmiarze.
- Powtórzone obserwacje QPSK mogą zmniejszać błąd dekodowania w niektórych
  kanałach; zysk zależy od niezależności błędów i kosztu opóźnienia.
- Współfaza/rezonans/konsensus mogą poprawiać odporność na wybrane
  zakłócenia, ale mogą też pogorszyć wynik i zawodzą przy skorelowanym echu.
- Architektura może mieć zastosowania badawcze w analizie sygnałów;
  nie wykazano przewagi nad rozwiązaniami standardowymi ani gotowości RF.

## Instrukcja wznowienia
1. Najpierw sprawdzić `README.md`, `docs/RELEASE_CHECKLIST.md`,
   `docs/HELIX_RELEASE_GATE.md` i ten dokument.
2. Nie dodawać algorytmów. Wybrać jedną wspieraną ścieżkę wydania:
   istniejące `helix_pro` + GUI; eksperymenty zostawić odseparowane.
3. Zweryfikować pakowanie, ręczne testy systemowe, zależności i klucze.
4. Dopiero po spełnieniu kryteriów wydać wersję/tag. Nie scalać całej
   gałęzi badawczej do `main` automatycznie.

Zasada: proste jest jak czołg. Ukończyć to, co działa; resztę zachować
jako hipotezy, nie obietnice.

## Nadrzędna zasada projektu — potwierdzona przez właściciela

Helix-Lock miał być **parasolem ochronnym, pancernym jak czołg**: możliwie
prosty, odporny i z minimalną powierzchnią ataku. Każdy nowy moduł może
wprowadzić kolejne słabości, więc nie należy go dodawać bez wyraźnej,
zweryfikowanej korzyści. Nie mnożyć warstw dla samego mnożenia warstw.

**Co rzeczywiście osiągnięto:** działający szyfrator plików AES-256-GCM,
GUI, przechodzące testy i zbudowane paczki na trzy platformy (bez pełnej
ręcznej walidacji); eksperymentalny HNS1 z ograniczonym użyciem pamięci;
wykrycie i naprawa części błędów starszych implementacji; udokumentowanie
granic heurystyk fazowych. **Czego nie dowiedziono:** przewagi
bezpieczeństwa nad dojrzałymi narzędziami, kompletnej odporności systemu
ani gotowego, niezależnie zaudytowanego produktu.

**Reguła na przyszłość:** „Pancerz nie musi mieć stu warstw. Musi mieć jak
najmniej miejsc, w których może pęknąć.” Zachować ten kierunek jako
kryterium każdej przyszłej decyzji projektowej.

## Wznowienie prac — 2026-11-09

Wznowiono prace na gałęzi `experiment/helix-native`, bez zmiany formatu
plików ani algorytmu AES.

- Podstawowy, wspierany `helix_pro/cipher.py` używa teraz wspólnego
  atomowego publikowania wyników: plik tymczasowy w katalogu docelowym,
  flush + fsync, a następnie `os.replace`. Dotyczy szyfrowania i
  odszyfrowywania formatów HLXP/HLXN. Chroni istniejący plik docelowy
  przed częściowym zapisem przy zwykłym błędzie procesu/systemu.
- Parser HLXP/HLXN odrzuca niepełny nagłówek jako `HelixProError`, zamiast
  wypuszczać nieobsłużony `IndexError`. Dodano minimalne kontrole długości
  przed KDF i próbą odszyfrowania.
- Testy regresji: awaria `os.replace`, błędny tag bez naruszenia
  poprzedniego pliku, ucięte nagłówki oraz poprawny round-trip.
  Dedykowane kroki testowe przeszły na Python 3.11 i 3.12 w workflow
  42545117592; pełny workflow nadal należy sprawdzić do końca.
- Zmiany nie obejmują HNS1, nie zmieniają formatu HLXP/HLXN i nie dodają
  nowej zależności. Nie dowodzą odporności na utratę zasilania (brak
  fsync katalogu), błędy sprzętowe ani złośliwe wyścigi na ścieżkach.

Zasada kontynuacji: najpierw wzmacniać i upraszczać wspólną ścieżkę
użytkownika; eksperymentalne funkcje pozostają odseparowane, dopóki
nie udowodnią korzyści bez zwiększania ryzyka.

### Kontynuacja — integracja atomowego zapisu z GUI

- Wspólny zapis został wystawiony jako `atomic_write_bytes()`.
- Domyślna aplikacja `helix_lock_app.py` używa go przy zapisie odszyfrowanej
  treści HLXN, zamiast bezpośredniego `open(..., "wb")`.
- Zachowana została również ścieżka legacy w `helix_pro_gui.py`; nie ma
  już odrębnego, nieatomowego zapisu odszyfrowanego HLXN w tych GUI.
- Dodano regresję dla publicznego writera, w tym zachowanie istniejącego
  pliku po symulowanej awarii publikacji.
- CI dla tych zmian: workflow 42545319529; w chwili zapisu oczekuje na
  zakończenie macierzy Python 3.11/3.12. Nie oznaczać jako zaliczonego,
  dopóki oba joby nie zakończą się sukcesem.

### Korekta CI po ekspozycji wspólnego writera

Pierwsze przebiegi integracyjne wykryły dwa błędy mechanicznej zmiany nazwy
funkcji writera (pozostałe odwołania do starej nazwy i brak importu w teście).
Zostały poprawione; nie był to błąd formatu ani kryptografii. Aktualny
przebieg dla kompletnego stanu po poprawkach: workflow
42545405156, commit `4620e4746565e063084158ee818d6370b9864771`.
Testy atomowego zapisu przeszły już na obu interpreterach; reszta długiej
macierzy nadal trwa. Nie uznawać całego CI za zielone przed zakończeniem
obu zadań.

### Wynik końcowy CI — integracja atomowego zapisu (2026-11-09)

Workflow [42545405156](https://github.com/jbackk-lang/Helix-Lock/actions/runs/42545405156)
dla commitu `4620e4746565e063084158ee818d6370b9864771` zakończył się sukcesem.
Oba zadania macierzy przeszły: Python 3.11 — 61/61 kroków; Python 3.12 —
61/61 kroków. Nie odnotowano nieudanych kroków.

Zakres tej serii:
- wspólny atomowy writer w `helix_pro/cipher.py`;
- użycie writera przez domyślne i legacy GUI przy publikacji odszyfrowanej
  treści HLXN;
- regresja zachowania istniejącego pliku przy symulowanej awarii replace;
- testy rdzenia i pełna macierz CI.

Ograniczenia: to nie potwierdza odporności na nagłą utratę zasilania,
wyścigi z wrogim procesem/systemem plików ani niezależnego audytu
bezpieczeństwa. Nadal wymagane są ręczne testy GUI na Windows/macOS/Linux.

### Dalsze wzmocnienie rdzenia i obsługi kluczy — 2026-11-09

- `encrypt_file_with_name()` publikuje teraz szyfrogram przez
  `atomic_write_bytes()`, tak samo jak HLXP i odszyfrowane dane.
  Nieudana publikacja nie powinna pozostawić częściowego szyfrogramu ani
  zastąpić poprzedniego celu.
- Dodano `write_new_key_file()`: plik klucza jest tworzony wyłącznie
  (`O_EXCL`), bez nadpisywania istniejącego klucza; na POSIX z trybem
  `0600`. Na Windows uprawnienia wynikają z ACL katalogu nadrzędnego.
- Oba GUI korzystają z bezpiecznego tworzenia klucza. Naprawiono też import
  helpera w głównym `helix_lock_app.py` i dodano test jego podłączenia.
- Testy sprawdzają: brak nadpisania klucza, tryb POSIX, atomowe
  szyfrowanie HLXN, zachowanie poprzedniego pliku po błędzie publikacji
  oraz import helperów w głównym GUI.
- CI dla stanu `d916ea3` (workflow 42545677927) przeszedł na Pythonie
  3.11 i 3.12 (61/61 kroków); test zrzutu GUI 42545677949 również przeszedł.
  Po ostatniej poprawce importu i dodaniu testu wiring workflow
  42545880781 uruchomiono na commicie `fe124a0`; wynik należy sprawdzić.
- Zrzut ekranu CI nie zastępuje ręcznego testu interakcji GUI na komputerze.

Ograniczenia pozostają: standardowy HLXP/HLXN nadal wczytuje cały plik do
pamięci; HNS1 jest eksperymentalny i nie jest zintegrowany z GUI. Atomic
replace + fsync pliku nie gwarantuje trwałości wpisu katalogowego po nagłej
utracie zasilania. Nie ma niezależnego audytu ani walidacji GUI na wszystkich
systemach. Nie należy deklarować gotowości produkcyjnej.

### Ochrona przed przypadkowym nadpisaniem źródła — 2026-11-09

Przegląd ścieżki GUI wykazał dodatkowy, praktyczny przypadek utraty danych:
użytkownik mógł wskazać ten sam plik (albo jego alias przez dowiązanie
symboliczne/twarde) jako źródło i cel deszyfrowania. Wspólny writer
atomowo zastąpiłby wtedy szyfrogram odzyskaną treścią. To nie jest błąd
AES, lecz niebezpieczna decyzja o ścieżce.

- Dodano `paths_refer_to_same_file()` w głównym GUI.
- Szyfrowanie i obie ścieżki deszyfrowania odrzucają cel wskazujący na
  ten sam plik źródłowy; kontrola obejmuje realpath, symlink i hardlink.
- Dodano testy aliasów; brak możliwości utworzenia dowiązania w środowisku
  testowym jest jawnie pomijany.
- Workflow 42545958309 uruchomiony dla testów regresji; wynik do sprawdzenia.

To chroni przed przypadkowym samonadpisaniem, ale nie zastępuje pełnej
ochrony przed wyścigami TOCTOU na współdzielonym systemie plików.

### Ochrona źródła w API kryptograficznym — 2026-11-09

Rozszerzono ochronę z GUI na publiczne API rdzenia:
- `ensure_distinct_paths()` odrzuca ten sam path, alias realpath,
  dowiązanie symboliczne i twarde.
- Ochrona jest stosowana w `encrypt_file()`, `decrypt_file()`,
  `encrypt_file_with_name()` i `decrypt_file_with_name()`.
- Testy potwierdzają, że zaszyfrowane źródło pozostaje nietknięte, gdy
  ktoś próbuje użyć go jako ścieżki wyjściowej, również przez kolizję
  oryginalnej nazwy pliku.
- Workflow 42546038843 uruchomiono dla pełnego zestawu testów po tej
  zmianie; przed uznaniem poprawki za zaliczoną sprawdzić oba joby.

### Wynik CI — ochrona przed nadpisaniem źródła (2026-11-09)

Workflow [42546038843](https://github.com/jbackk-lang/Helix-Lock/actions/runs/42546038843)
dla kodu z commitu `3c546a2496d895c4e42ab732b9fdd05cfff20bfd` zakończył się
sukcesem: Python 3.11 — 61/61 kroków; Python 3.12 — 61/61 kroków.
Oba joby bez błędów. Obejmuje testy rdzenia, testy aliasów ścieżek oraz
pełną istniejącą macierz AIRP/eksperymentów.

### Walidacja nazw plików w formacie HLXN — 2026-11-09

Dodano wspólną walidację nazwy zapisanej wewnątrz uwierzytelnionego
payloadu. Nowe szyfrowanie HLXN odrzuca ścieżki zamiast pojedynczej nazwy,
separatory obu systemów, znaki sterujące, nazwy urządzeń Windows
(CON/NUL/COM1/LPT1 itd.) oraz nazwy kończące się spacją lub kropką.
Odszyfrowywanie sprawdza to samo pole po uwierzytelnieniu i odrzuca
niebezpieczne lub nieprzenośne metadane zamiast zapisywać je na dysku.
Dodano testy parametrów dla traversal, ADS/kolonów i nazw urządzeń.
Workflow 42546259891 uruchomiono; wynik oczekuje na zakończenie obu
interpreterów. Ograniczenie kompatybilności: pliki HLXN ze starszym,
nieprzenośnym oryginalnym basename mogą teraz zostać odrzucone.

### HNS1: kontrola aliasów plików — 2026-11-09

Przegląd eksperymentalnego, ograniczonego pamięciowo HNS1 ujawnił brak
jawnej kontroli dowiązań twardych w odróżnieniu od głównego API. Dodano
wspólną kontrolę wejścia/wyjścia przed szyfrowaniem i deszyfrowaniem:
ścieżka, realpath/symlink i `os.path.samefile()`. Test sprawdza oba
kierunki i potwierdza zachowanie zawartości źródła. HNS1 pozostaje
eksperymentalny i nie jest promowany do domyślnego GUI; wymaga osobnej
oceny formatu, cyklu klucza i kompatybilności.
Workflow 42546501311 uruchomiono dla testów HNS1 oraz pełnej macierzy.

### Wynik CI — eksperymentalny HNS1 i aliasy hardlink (2026-11-09)

Workflow 42546569335 dla commitu `39525ac` zakończył się sukcesem:
Python 3.11 i 3.12 — po 61/61 kroków. Potwierdzono kontrolę aliasów
w HNS1 po poprawce helpera; pierwsza iteracja testu wykryła błąd
integracji (helper wywoływał sam siebie i kontrola nie była stosowana
w obu ścieżkach). Zostało to naprawione i zielone CI potwierdza poprawkę.
To dobra regresja: test zatrzymał błąd, zanim zmiana została uznana za
gotową.

Dodatkowo walidacja nazw HLXN odrzuca teraz wszystkie znaki Unicode
kategorii Cc i normalizuje początkowy człon nazwy przed sprawdzeniem
zarezerwowanych nazw urządzeń Windows, a jednocześnie dopuszcza zwykłe
spacje w nazwie. Rozszerzone testy są w workflow 42546705983 — wynik
oczekuje na zakończenie macierzy.

### Wieloplatformowy build aplikacji desktopowej — 2026-11-09

Workflow [42546762025](https://github.com/jbackk-lang/Helix-Lock/actions/runs/42546762025)
zbudował aplikację PyInstaller bez błędów na trzech systemach:
- Linux — artefakt `HelixLock-linux` (31,189,032 B)
- Windows — artefakt `HelixLock-windows` (16,175,575 B)
- macOS — artefakt `HelixLock-macos` (14,944,620 B)

Artefakty są dostępne jako wyniki CI (retencja 30 dni); nie jest to jeszcze
wydanie podpisane ani opublikowane. Build potwierdza pakowanie, nie test
instalacji/uruchomienia na rzeczywistym komputerze. Nie twórz taga release
przed ręcznym smoke-testem GUI i weryfikacją kluczy/aktualizacji.
