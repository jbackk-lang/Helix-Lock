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
