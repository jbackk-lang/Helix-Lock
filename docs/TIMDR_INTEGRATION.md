# TIMDR w Helix-Lock — mapa pochodzenia i plan integracji

**Status:** projekt integracji / hipotezy inżynierskie. Nie jest deklaracją, że TIMDR zastępuje kryptografię ani że jego operatory zostały już zwalidowane dla bezpieczeństwa kryptograficznego.

## 1. Korekta opisu pochodzenia

Helix-Lock należy traktować jako projekt rozwijany w ekosystemie GIA/TIMDR. Wcześniejsza odpowiedź zbyt wąsko opisała relację: stwierdzenie, że TIMDR nie został wykorzystany, pomija możliwe pochodzenie architektury, modelu informacji i mechanizmów AIRP/rotacji/ciągłości.

Jednocześnie dostępny w repozytorium historyczny moduł `old/helix_lock_cipher.py` pokazuje, że pierwotna implementacja szyfrowania używała bezpośrednio AESGCM z biblioteki `cryptography`. Aktualny `helix_pro/cipher.py` nadal deleguje prymityw szyfrujący do AES-256-GCM. To opis implementacji prymitywu, a nie pełnego pochodzenia projektu.

Wniosek: trzeba rozdzielić **pochodzenie koncepcji i architektury** od **konkretnego prymitywu kryptograficznego**. TIMDR może organizować model stanu, historię, kontrolę przejść i politykę rotacji; AES-GCM zapewnia poufność i uwierzytelnienie danych. Te role nie są konkurencyjne.

## 2. Mapowanie istniejących elementów

| Element Helix-Lock | Możliwe odniesienie TIMDR | Status |
|---|---|---|
| AIRP event ledger, sekwencja, hash poprzednika | Chronoproces / wspólny nośnik zdarzeń; projekcja M/S jako przebieg zmian | Kandydat architektoniczny; wymaga jawnego adaptera i testów |
| Wersja obiektu i CAS w AIRPStore | stan obiektu i kontrola dozwolonych przejść | Zgodność inżynierska, nie nowy aksjomat |
| CounterLock | monotoniczna obserwacja kolejnych zdarzeń/odczytów | Nie utożsamiać licznika z czasem TIMDR ani dowodem braku rollbacku |
| Fingerprint klucza i ciphertextu | niezmiennik / obserwowalna cecha reprezentacji | SHA-256 służy identyfikacji; nie jest kluczem ani dowodem autentyczności |
| AIRP key rotation | kontrolowane przejście pomiędzy wersjami reprezentacji | Kandydat do nadzoru przez politykę przejść |
| Quorum / zewnętrzne kotwice | niezależne świadectwa stanu | Warstwa zaufania; nie jest automatycznie gałęzią TIMDR |
| AES-256-GCM | prymityw poufności i integralności | Pozostaje standardowym prymitywem; TIMDR go nie zastępuje |

## 3. Zasada nieredukowalności gałęzi

Nie wolno tworzyć jednego „wektora TIMDR” przez arbitralne sklejenie M/S, G, K i META-DYNAMICS. Zgodnie z architekturą GIA-TIMDR, gałęzie mają odrębne obiekty i operatory. Dla Helix-Lock pierwszym kandydatem jest projekcja zdarzeń AIRP do gałęzi M/S, o ile dane rzeczywiście tworzą uporządkowany szereg czasowy z ustaloną semantyką. Chronoproces może pełnić rolę orkiestracji projekcji, ale nie uzasadnia utożsamienia ich znaczeń.

Gałąź G lub K nie powinna być dodawana tylko dlatego, że nazwa produktu zawiera „Helix”. Geometria Möbiusa/helisy nie jest sama w sobie dowodem przydatności geometrycznego operatora do ochrony danych.

## 4. Proponowany adapter — bez wpływu na szyfrowanie

Wydzielony adapter może przyjmować wyłącznie metadane zdarzeń, bez kluczy, haseł, plaintextu ani surowego ciphertextu:
- sekwencję i czas zdarzenia;
- typ zdarzenia (encrypt, decrypt, verify, rotate, quorum_pending, quorum_confirmed, rollback_rejected);
- identyfikator obiektu i wersję;
- wynik kontroli integralności / CAS;
- identyfikator pseudonimowy, bez danych osobowych.

Adapter buduje jawnie zdefiniowany szereg obserwacji. Nie interpretuje pojedynczego nieudanego logowania jako ataku. Nie zmienia danych, kluczy ani decyzji kryptograficznych.

## 5. Hipotezy do prerejestracji i falsyfikacji

H1: przebieg metadanych zdarzeń AIRP zawiera mierzalne anomalie M/S poprzedzające niespójne przejścia wersji.

H2: detekcja TIMDR wnosi wartość ponad proste baseline'y: licznik nieudanych operacji, reguły CAS, kontrolę podpisu, alarmy quorum i klasyczne statystyki okienkowe.

H3: alarm TIMDR nie generuje nieakceptowalnej liczby fałszywych alarmów podczas legalnych operacji masowych, restartów, synchronizacji i rotacji kluczy.

Dla każdej hipotezy należy przed testem zamrozić definicje, progi, okna, metrykę, dane treningowe/kalibracyjne i holdout. Wymagane są kontrola pozytywna, kontrola negatywna, test na tle losowym, moc testu, wielkość efektu i raport wyniku negatywnego. Nie wolno dostrajać progów po obejrzeniu holdoutu.

## 6. Granice bezpieczeństwa

- TIMDR nie szyfruje i nie zastępuje AES-256-GCM.
- Alarm TIMDR może co najwyżej uruchomić bezpieczną reakcję polityki: wstrzymanie operacji, wymaganie ponownej autoryzacji, zapis zdarzenia lub rozpoczęcie zatwierdzonej rotacji.
- Nie wolno zmieniać plaintextu ani klucza w reakcji na błędne hasło, nieudaną autentykację lub sam alarm statystyczny.
- Rotacja nie unieważnia kopii klucza/ciphertextu, które napastnik już posiada.
- Licznik lokalny bez zewnętrznego, odpornego na rollback źródła prawdy nie dowodzi, że historia nie została cofnięta.
- Moduł analityczny powinien działać fail-safe: awaria analizy nie może osłabiać uwierzytelnienia ani ujawniać danych.

## 7. Plan implementacji

1. Udokumentować mapę pochodzenia: koncepcje TIMDR, elementy AIRP i standardowe prymitywy kryptograficzne.
2. **Zaimplementowano:** opcjonalny moduł `helix_pro/timdr_adapter.py`, który przyjmuje wyłącznie metadane zdarzeń i wylicza opisowe cechy M/S.
3. **Dodano testy:** `tests/test_timdr_adapter.py` obejmuje deterministyczność, brak odczytu pól sekretów, monotoniczność sekwencji, strefy czasowe i walidację okna. Testy wymagają uruchomienia w CI.
4. Następnie przygotować prerejestr testu H1–H3 oraz baseline'y.
5. Uruchomić eksperyment na syntetycznych śladach i odrębnym holdoucie rzeczywistych logów pozbawionych sekretów.
6. Dopiero po wynikach zdecydować, czy adapter zostaje funkcją diagnostyczną. Nie podnosić go do mechanizmu bezpieczeństwa bez dowodów.

## 8. Źródła w ekosystemie

- GIA-TIMDR: `ARCHITEKTURA_TIMDR.md`, `SKILL_timdr-signal-framework.md`, `TIMDR_Branch_Specification.md`.
- Chronoproces: `TIMDR-Time-Formalism/timdr_time/chronoprocess.py`.
- Helix-Lock: `helix_pro/cipher.py`, `helix_pro/airp_store.py`, `helix_pro/airp_ledger.py`, `helix_pro/airp_monitor.py`, `helix_pro/adaptive_rotation.py`, `helix_pro/counter_lock.py`, `old/helix_lock_cipher.py`.

**Zasada raportowania:** rozróżniaj „koncepcja pochodzi z TIMDR”, „adapter implementuje projekcję”, „test kodu przeszedł”, „hipoteza empiryczna wsparta” i „właściwość bezpieczeństwa udowodniona”. To pięć różnych twierdzeń.
