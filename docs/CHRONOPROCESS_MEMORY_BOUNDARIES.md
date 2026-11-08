# Chronoproces, pamięć historii i granice samoregulacji

**Data:** 2026-11-08  
**Status:** audyt architektury i plan eksperymentów; bez zmiany prymitywu kryptograficznego.

## 1. Najważniejsze ustalenie z GIA-TIMDR

Aktualny `Chronoprocess` w `GIA-TIMDR/TIMDR-Time-Formalism/timdr_time/chronoprocess.py` jest orkiestratorem trzech niezależnych rzutów wspólnego nośnika `T`:

- M/S: tempo i drift znaczników czasu;
- G: kongruencja powierzchniowa `Gamma(T x I)`;
- K: faza i interferencja modalności oceniane w punktach `T`.

Zasada nieredukowalności gałęzi jest jawna: te trzy rzuty nie są utożsamiane. Sam Chronoproces nie przechowuje historii zdarzeń, nie definiuje sprzężonej dynamiki pętli i nie implementuje prawa samonaprawy. Gałąź K korzysta z modalności o stałych parametrach; nieliniowe sprzężenie wymagałoby osobnego formalizmu i walidacji.

## 2. Co już istnieje w Helix-Lock

| Komponent | Rzeczywista rola | Ograniczenie |
|---|---|---|
| AIRPIntegrityLedger | trwały, hash-chain dziennik zdarzeń i podpisane checkpointy | lokalny łańcuch sam nie chroni przed rollbackiem; potrzebna niezależna kotwica |
| AIRPMonitor | bieżący stan reprezentacji i ograniczony bufor ostatnich zdarzeń | bufor jest procesowy i stratny; nie zastępuje audytu |
| TIMDR adapter | projekcja metadanych zdarzeń na niepokrywające się okna M/S | cechy opisowe; nie jest detektorem ani reakcją bezpieczeństwa |
| Chronoprocess | wspólny nośnik i delegacja do trzech gałęzi TIMDR | nie jest obecnie pamięcią adaptacyjną ani regulatorem faz |

Wniosek: ograniczenie bufora monitora rozwiązuje wzrost pamięci RAM, ale nie rozwiązuje problemu semantycznej pamięci historii. Z kolei ledger zachowuje historię, lecz jego przechowywanie jest celowo trwałe i nie powinno być bezrefleksyjnie „kompresowane” przez usuwanie zdarzeń.

## 3. Trzy odrębne znaczenia pamięci

1. **Pamięć audytowa:** dokładna sekwencja zdarzeń, weryfikowalna przez łańcuch hashy i zewnętrzne checkpointy. Nie wolno jej zastępować stratnym streszczeniem.
2. **Pamięć operacyjna:** ograniczony bufor ostatnich zdarzeń, który może być nadpisywany; jawnie raportuje liczbę usuniętych wpisów.
3. **Pamięć cech historycznych:** pochodne, ograniczone podsumowania okien czasowych (np. tempo, drift, rozkład typów zdarzeń). Mogą służyć analizie trendu, ale muszą zachować pochodzenie: zakres sekwencji, zakres czasu, wersję algorytmu i hash źródłowego checkpointu.

Nie należy utożsamiać żadnego z tych poziomów z pamięcią fazową ani z rekonstrukcją informacji.

## 4. Istotny wynik dotychczasowego eksperymentu czasu

Eksperyment `chronoprocess_triple_loop_time_history.py` pokazuje, że po czasowym odstrojenia częstotliwości chwilowa częstotliwość może wrócić do wartości nominalnej, podczas gdy skumulowane relacje fazowe nadal zachowują ślad zaburzenia. Zaburzenie wspólne dla wszystkich trzech kanałów zachowuje relacje względne — to kontrola common-mode, nie samonaprawa.

Eksperyment nie zawiera sprzężenia zwrotnego. Dlatego nie dowodzi samonaprawy. Osobny model Kuramoto wykazuje relaksację fazową przy zadanym sprzężeniu, ale jest to dodatkowy model kandydujący, a nie zachowanie wynikające z aktualnego Chronoprocesu.

## 5. Bezpieczny kierunek implementacji pamięci historycznej

- Zachować ledger jako źródło prawdy; nie usuwać ani nie przepisywać historycznych zdarzeń w ramach kompresji.
- Budować podsumowania w osobnym, wersjonowanym strumieniu/artefakcie.
- Każde podsumowanie wiązać z zakresem sekwencji, zakresem czasu, parametrami ekstrakcji i hashami checkpointów.
- W razie potrzeby ograniczać pamięć RAM przez agregaty przyrostowe, ale zachować możliwość ponownego wyliczenia z ledgeru.
- Oddzielić sygnał analityczny od decyzji autoryzacyjnej. Alarm statystyczny nie może zmieniać kluczy, plaintextu ani treści szyfrogramu.
- Nie nazywać agregacji „samoregeneracją”. To pamięć cech; samoregulacja wymaga osobnego, jawnego prawa dynamiki.

## 6. Plan testów

A. **Reprodukowalność:** ten sam ledger i wersja ekstraktora dają identyczne podsumowania niezależnie od wielkości partii wejściowych.

B. **Ciągłość:** brakujące, powtórzone lub przestawione sekwencje są wykrywane; podsumowanie wskazuje dokładny zakres wejściowy.

C. **Odporność na wzrost:** zużycie RAM agregatora nie rośnie liniowo z całkowitą liczbą zdarzeń, przy zachowaniu stałego rozmiaru stanu roboczego.

D. **Wierność:** podsumowania nie są używane do odtworzenia payloadu; integralność payloadu nadal weryfikuje AEAD i hash źródłowy.

E. **Chronoproces:** dopiero po mapowaniu rzeczywistych zmiennych TSI/TIMDR można badać, czy podsumowania historyczne mają interpretację w konkretnych gałęziach M/S, G lub K. Nie sklejać ich w arbitralny wspólny wektor.

## 7. Kryterium wniosku

Pamięć historyczna może poprawiać wykrywanie zmian lub interpretację kolejnych przejść. Nie oznacza to automatycznie, że system potrafi odzyskać utraconą informację. Każdy raport musi oddzielać: integralność, koherencję fazową, ciągłość historii, rekonstrukcję treści i jakość decyzji.

**Zasada:** kompresujemy reprezentację analityczną, nigdy nie niszczymy źródłowej historii ani nie udajemy, że streszczenie jest oryginałem.


## 8. Pierwsza implementacja pamięci cech historycznych

Dodano `helix_pro/airp_history_memory.py` (`AIRPHistoryMemory`) i `tests/test_airp_history_memory.py`.

Implementacja:
- konsumuje uporządkowane zdarzenia partiami;
- wymaga ciągłych numerów sekwencji i strefowych znaczników czasu;
- tworzy niepokrywające się, stałe okna;
- emituje deterministyczne podsumowania z zakresem sekwencji, czasem, licznikami typów, odmowami, rotacjami, statystykami odstępów i hashem podsumowania;
- wiąże wynik z SHA-256 zewnętrznego checkpointu źródłowego przekazanego przez wywołującego;
- nie zachowuje payloadów, identyfikatorów obiektów ani kryptograficznych sekretów.

**Ograniczenie pamięci:** obiekt przechowuje najwyżej niepełne okno (maksymalnie `window_size` lekkich rekordów). Gotowe podsumowania są zwracane wywołującemu i nie są akumulowane w obiekcie. Warstwa wywołująca musi zapisać je w osobnym magazynie. Dzięki temu pamięć robocza jest O(window_size), a nie O(liczby zdarzeń).

**Granica zaufania:** klasa nie weryfikuje samodzielnie, czy podany hash checkpointu jest prawidłowym, podpisanym checkpointem ani czy obejmuje ostatni przetworzony numer sekwencji. To musi zapewnić integracja z `AIRPIntegrityLedger.verify()/verify_checkpoint()` i niezależnym `TrustAnchor`. Podsumowanie jest indeksem analitycznym, nigdy źródłem prawdy, dowodem autoryzacji ani materiałem do rekonstrukcji payloadu.

Testy obejmują równoważność przetwarzania partiami, stały limit stanu roboczego, wykrywanie luk/replay, odrzucanie naiwnych timestampów oraz brak wycieku payloadu/ID do podsumowań.
