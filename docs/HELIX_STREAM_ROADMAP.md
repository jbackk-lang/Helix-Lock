# Helix Stream — kierunek rozwoju i plan techniczny

**Gałąź:** `feature/helix-stream-core`  
**Punkt startowy:** `experiment/helix-native`  
**Status:** prace badawczo-inżynierskie; brak deklaracji gotowości produkcyjnej.

## Cel

Wydzielić z Helix-Lock mały, niezależny rdzeń do szyfrowania danych w locie: komunikatów, strumieni i danych przesyłanych pomiędzy aplikacjami. Priorytetem są bezpieczeństwo, małe zużycie pamięci, przewidywalne opóźnienia i prosta integracja.

Nie budujemy nowego szyfru. Poufność i integralność zapewnia standardowe, uwierzytelnione szyfrowanie (AEAD) z dojrzałej biblioteki. „Helix” opisuje projekt i ewentualne eksperymenty z reprezentacją/przetwarzaniem, nie własny prymityw kryptograficzny.

## Podział repozytorium

| Gałąź | Odpowiedzialność | Zasada |
|---|---|---|
| `experiment/helix-native` | Helix File: aplikacja desktopowa, GUI, HLXN/HLXP, kolejka plików, AIRP i CounterLock | Stabilizować istniejący przepływ plików; nie dodawać tu eksperymentów transmisyjnych |
| `feature/helix-stream-core` | Helix Stream: kodowanie/szyfrowanie w locie, rekordy, strumienie, adaptery transportowe i benchmarki | Rozwijać niezależnie; nie zmieniać formatów plikowych bez potrzeby |
| `main` | Linia główna | Bez automatycznego merge; integracja dopiero po przeglądzie i testach |

Wspólny kod kryptograficzny może zostać wydzielony dopiero po określeniu stabilnego interfejsu i testów zgodności. Na początku nie kopiować i nie modyfikować bez potrzeby istniejącego szyfru plikowego.

## Co już istnieje

- `helix_pro/cipher.py`: obsługiwane formaty plikowe HLXN/HLXP oparte na AES-256-GCM; nie są protokołem sieciowym.
- `experiments/helix_stream_envelope.py`: prototyp HNS1, rekordy po 64 KiB, AES-GCM, licznik sekwencji i uwierzytelniony rekord końcowy; strumieniowy zapis/odczyt do plików.
- `tests/test_helix_stream_envelope.py`: round-trip, błędny klucz, modyfikacja, ucięcie, dopisanie danych, aliasy plików.
- `tests/test_helix_stream_stress.py`: test 12 MiB i pomiar pamięci Python heap, przerwanie procesu przed publikacją wyniku.

To dobry punkt startowy, ale HNS1 pozostaje prototypem plikowym. Nie ma jeszcze zarządzania sesją/kluczami, ochrony replay na poziomie aplikacji, negocjacji wersji, kontroli przepływu ani adaptera sieciowego. 64-bitowy losowy prefiks nonce nie powinien być bez analizy przyjęty jako docelowy plan unikalności dla długotrwałego lub wielosesyjnego użycia tego samego klucza.

## Bieżący postęp — 9 listopada 2026

**S0:** prototyp HNS1 i jego testy zachowane jako baseline.

**Część S2 — pierwszy eksperymentalny komponent rekordowy:**
- `helix_stream/records.py` udostępnia `RecordSealer` i `RecordOpener`;
- rekordy mają jawny typ, numer sekwencji i długość;
- AES-256-GCM uwierzytelnia nagłówek wraz z identyfikatorem sesji i etykietą kierunku;
- rozmiar danych w rekordzie jest ograniczony do 64 KiB;
- odbiorca odrzuca ucięcie, zmianę kolejności, powtórzenie, zmianę metadanych i dane po rekordzie końcowym;
- osobny workflow CI testuje Python 3.11 i 3.12.

**Wynik CI dla pierwszego zestawu:** obie wersje Pythona przeszły testy. Po zaostrzeniu fixture'ów testowych uruchamiany jest kolejny przebieg.

**Ograniczenia:** to prototyp niskopoziomowego framingu, nie gotowy protokół. Klucz musi być świeży i niezależny dla każdej sesji oraz kierunku; nie wolno resetować sekwencji i ponownie używać klucza. Ustanawianie kluczy, uwierzytelnianie peerów, trwała ochrona replay po reconnect, kontrola przepływu i transport nie są jeszcze zaimplementowane. Odbiorca dostaje każdy poprawnie uwierzytelniony rekord danych przed rekordem końcowym; aplikacja musi odróżniać poprawność pojedynczego rekordu od kompletności całego strumienia.

## Architektura docelowa

1. **API strumienia** — interfejs źródła/odbiornika bajtów, bez zależności od GUI, systemu plików lub konkretnego transportu.
2. **Framing** — jawna wersja, typ rekordu, długość, numer sekwencji i ograniczenia rozmiaru; parser odporny na fragmentację, sklejenie i niekompletne wejście.
3. **Sesja i klucze** — ustanawianie kluczy przez sprawdzony protokół/standard, separacja kierunków, rotacja i limity; żadnych własnych uzgodnień kryptograficznych.
4. **AEAD** — uwierzytelnianie nagłówków i danych, unikalność nonce pod danym kluczem, odrzucanie błędów bez ujawniania częściowych danych.
5. **Replay i kolejność** — kontrola sekwencji, duplikatów, cofnięcia i wznowienia sesji; stan replay przypisany do sesji, nie globalny licznik bez kontekstu.
6. **Backpressure** — ograniczone bufory, limity kolejki, anulowanie i kontrola tempa; odbiorca nie może być zmuszony do nieograniczonego zużycia pamięci.
7. **Transport** — adaptery TCP/QUIC/WebSocket lub IPC jako osobna warstwa. Jeśli TLS 1.3/QUIC już spełnia wymagania, preferować standardowy kanał zamiast dublować protokół.
8. **Obserwowalność** — pomiar opóźnienia, przepustowości, pamięci, utraty, ponowień i błędów bez logowania kluczy ani plaintextu.

## Etapy prac i bramki

### S0 — zamrożenie baseline'u
- zachować HNS1 jako prototyp porównawczy;
- odtworzyć wszystkie istniejące testy;
- zanotować wersję Pythona, biblioteki kryptograficznej, system i parametry testu.

**Wyjście:** powtarzalny baseline; brak regresji.

### S1 — kontrakt protokołu i model zagrożeń
- określić, czy wymagamy ochrony end-to-end ponad TLS, czy tylko bezpiecznego transportu;
- zdefiniować granice sesji, uwierzytelnienie peerów, model replay, reconnect i rotację kluczy;
- spisać limity rozmiarów, liczników, buforów i błędów;
- wybrać standard ustanawiania kluczy, nie projektować własnego.

**Wyjście:** przegląd modelu zagrożeń i specyfikacja rekordu przed kodem sieciowym.

### S2 — rdzeń rekordowy bez sieci
- parser inkrementalny obsługujący częściowe wejścia i wiele rekordów w jednym buforze;
- AEAD z kluczami sesyjnymi i rozdzieleniem kierunków;
- jawna obsługa końca strumienia, błędów i limitów;
- brak publikacji niezweryfikowanych danych.

**Wyjście:** testy wektorów, mutacji, ucięć, przepełnień, duplikatów i zmiany kolejności.

### S3 — testy wydajności i pamięci
Porównać z TLS 1.3/QUIC oraz prostym AES-GCM na tych samych danych i sprzęcie:
- MiB/s i wiadomości/s;
- p50/p95/p99 opóźnienia;
- CPU, RAM/peak heap i rozmiar buforów;
- wpływ wielkości rekordu i rozmiaru wiadomości;
- koszt inicjalizacji sesji i rotacji kluczy.

**Wyjście:** powtarzalny wynik z kodem, sprzętem, wersjami i surowymi danymi. Bez twierdzeń o przewadze na podstawie pojedynczego testu.

### S4 — adapter transportowy
- najpierw lokalny socket/test loopback;
- potem jeden transport wskazany wymaganiami;
- backpressure, reconnect i timeouty;
- testy współbieżności i limitów zasobów.

**Wyjście:** niezawodna transmisja w warunkach testowych, bez naruszeń modelu sesji.

### S5 — decyzja o wdrożeniu
Wdrożyć tylko wtedy, gdy Helix Stream rozwiązuje konkretny problem, którego nie rozwiązuje wystarczająco dobrze TLS 1.3/QUIC, i nie pogarsza bezpieczeństwa. W przeciwnym razie dostarczyć lekką bibliotekę nad standardowym transportem albo zamknąć eksperyment.

## Kryteria bezpieczeństwa — blokujące

- Brak własnego szyfru, KDF, wymiany kluczy i ręcznie projektowanego AEAD.
- Nonce nigdy nie powtarza się pod tym samym kluczem; rotacja i limity są jawne.
- Nagłówki krytyczne są uwierzytelnione jako AAD.
- Replay, duplikaty, zmiana kolejności i reconnect mają określone zachowanie.
- Nie zwracać ani nie przekazywać częściowo zweryfikowanego plaintextu jako zaufanego.
- Parser ma limity długości, czasu i pamięci; odporność na DoS jest testowana.
- Klucze i plaintext nie trafiają do logów, telemetryki ani repozytorium.
- Niezależny przegląd przed użyciem produkcyjnym.

## Otwarte decyzje

1. Czy pierwszym przypadkiem użycia są komunikaty aplikacyjne, ciągły strumień danych, czy pliki przesyłane fragmentami?
2. Czy potrzebne jest szyfrowanie end-to-end ponad TLS, czy wystarczy TLS 1.3?
3. Czy wymagane są komunikacja dwukierunkowa, wiele równoległych sesji i wznowienie po zerwaniu?
4. Jaki jest docelowy sprzęt, język integracji i budżet opóźnienia?
5. Czy jakikolwiek eksperyment fazowy wnosi mierzalną korzyść względem zwykłego framingu? Dopóki nie ma dowodu, nie wchodzi do ścieżki bezpieczeństwa.

## Reguła projektu

Najpierw prosty, poprawny i audytowalny strumień. Potem pomiary. Dopiero na końcu optymalizacja. Helix Stream nie może osłabić Helix File ani zwiększać powierzchni ataku bez wykazanej korzyści.
