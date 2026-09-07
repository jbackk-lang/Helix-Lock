# Helix‑Lock

Warstwa ochronna świadomości i treści.
Zamyka skręt, odcina szum, przepuszcza tylko kierunek.

Helix‑Lock to szyfrator plików oparty na AES-256-GCM (biblioteka
`cryptography`, audytowana, standardowa) — nazwa nawiązuje do „skrętu
helisy”, ale pod spodem to zwykłe, sprawdzone uwierzytelnione
szyfrowanie, nie autorska kryptografia.

## Zacznij tutaj: `helix_pro/`

To jest aktualna, zalecana wersja. Wcześniejsze moduły (`old/`) zostały
zarchiwizowane 2026-08 po audycie, który znalazł w nich konkretne błędy
(patrz niżej) — `helix_pro/` je naprawia i jest jedynym miejscem, z
którego warto dziś korzystać.

```python
from helix_pro import generate_key, encrypt_file_with_name, decrypt_bytes_with_name

# tryb pliku-klucza (najsilniejszy - przechowuj klucz OSOBNO od danych)
key = generate_key()
encrypt_file_with_name("zdjecie.jpg", "wynik.helixpro", key=key)

# oryginalna nazwa (a wiec i rozszerzenie/typ pliku) jest zapisana
# WEWNATRZ zaszyfrowanej tresci - wraca poprawnie nawet jesli plik
# .helixpro zostal po drodze przemianowany:
name, content = decrypt_bytes_with_name("wynik.helixpro", key=key)
assert name == "zdjecie.jpg"

# albo tryb hasła (sól zapisana w nagłówku pliku, samo hasło musi być silne)
encrypt_file_with_name("dane.txt", "dane.helixpro", password="bardzo-dlugie-haslo")
```

Prostszy wariant bez zapisywania nazwy (`encrypt_file`/`decrypt_file`,
identyczne API) też jest dostępny, jeśli nazwa pliku ma zostać ustalona
ręcznie przez wywołujący kod.

`encrypt_file_with_name` domyślnie (`compress=True`) próbuje gzip PRZED
szyfrowaniem — najpopularniejszy, wbudowany w Pythona format kompresji.
"Smart": gzip jest użyty tylko wtedy, gdy faktycznie zmniejsza dane —
dla już skompresowanych formatów (jpg, mp4, zip...) plik wynikowy nigdy
nie jest większy niż bez próby kompresji, bo w takim wypadku dane trafiają
do środka surowe. Ustaw `compress=False`, żeby pominąć próbę w ogóle.

Działa na dowolnym typie pliku (tekstowy, binarny, obraz, cokolwiek) —
zweryfikowane na losowych danych binarnych, tekście z polskimi znakami,
pliku z powtarzalnym wzorcem bajtów i pliku pustym: wynik zawsze
bajt-w-bajt identyczny z oryginałem, narzut to stałe 34 bajty niezależnie
od rozmiaru i typu pliku (`encrypt_file`/`decrypt_file`; wariant `_with_name`
dolicza jeszcze 1 bajt + długość nazwy).

Drugi moduł, `helix_pro.CounterLock` — licznik odczytów kryptograficznie
związany z treścią (zamiast osobnego podpisu nad jawnym base64, jak w
starym `HLX1.py`). Niskopoziomowe API działa na samych bajtach:

```python
from helix_pro import generate_key, CounterLock

lock = CounterLock(generate_key())
blob = lock.lock(b"wiadomosc", counter=0)
data, counter, next_blob = lock.unlock_and_advance(blob)
```

...a wysokopoziomowe funkcje plikowe (te same, których używa checkbox
"Śledź licznik odczytów" w GUI — patrz sekcja GUI niżej) odtwarzają też
nazwę/rozszerzenie i nadpisują plik źródłowy nową wersją licznika przy
każdym odszyfrowaniu:

```python
from helix_pro import generate_key, encrypt_file_with_counter, decrypt_file_with_counter

key = generate_key()
encrypt_file_with_counter("dane.txt", "dane.helixpro", key=key)  # counter=0

# kazde wywolanie ponizej nadpisuje "dane.helixpro" wyzszym licznikiem
out_path, counter_before = decrypt_file_with_counter("dane.helixpro", "odzyskane/", key=key)
```

### 🔐 Właściwości kryptograficzne (co i dlaczego)

- **Nonce.** Każde szyfrowanie generuje nowy, losowy 96-bitowy nonce
  (`os.urandom(12)`) — zweryfikowane empirycznie: ten sam plik, ten sam
  klucz, zaszyfrowany dwukrotnie, daje za każdym razem inny wynik
  (różne nonce w nagłówku, różny cały ciphertext). W trybie hasła sól
  do scrypt też jest losowa i świeża przy każdym szyfrowaniu (patrz test
  `test_encrypt_file_password_mode_uses_random_salt_each_time`) —
  identyczne pliki nigdy nie szyfrują się identycznie.
- **Tag autentykacji (AEAD).** AES-GCM dolicza do ciphertextu tag
  integralności — zmiana pojedynczego bajtu ciphertextu, nonce albo
  nazwy pliku (w wariancie `_with_name`, bo nazwa jest częścią
  szyfrowanej treści) powoduje, że odszyfrowanie rzuca `HelixProError`
  zamiast po cichu zwrócić zmanipulowane dane. Zweryfikowane testem
  `test_tampered_ciphertext_is_rejected`.
- **Kompresja przed szyfrowaniem.** `encrypt_file_with_name` domyślnie
  próbuje gzip przed AES-GCM (patrz sekcja o kompresji wyżej). Realna,
  zweryfikowana korzyść to mniejszy plik — nie bezpieczeństwo.
- **Licznik odczytów (`CounterLock`) — opt-in, nie domyślna ścieżka.**
  To NIE jest coś, co dzieje się automatycznie przy zwykłym
  `encrypt_file_with_name`/`decrypt_file` — trzeba świadomie włączyć tę
  opcję (`encrypt_file_with_counter`/`decrypt_file_with_counter`, albo
  checkbox "Śledź licznik odczytów" w GUI — patrz sekcja GUI niżej).
  Dokładniejsze sformułowanie tego, co faktycznie robi: licznik jest
  wpięty jako AAD w AES-GCM, więc odblokowanie wykrywa PODMIENIONY w
  nagłówku licznik (ktoś podmienił sam nagłówek bez ponownego
  szyfrowania) i pozwala zauważyć więcej udanych odblokowań niż się
  spodziewałeś, JEŚLI wywołujący kod zapamiętał ostatnio widziany
  licznik i go porównuje — obecne GUI tego porównania jeszcze nie robi,
  tylko pokazuje licznik "przed" w statusie po każdym odszyfrowaniu
  (patrz `test_decrypt_file_with_counter_rejects_rolled_back_copy`,
  które wprost dokumentuje ten brak automatycznego porównania).
  To NIE wykrywa prób brute-force klucza — atakujący bez klucza nigdy
  nie dojdzie do etapu odczytania/inkrementacji licznika (AES-GCM
  odrzuca złe klucze na etapie autentykacji, przed dotarciem do
  jakiejkolwiek treści) — każda nieudana próba po prostu kończy się
  błędem, nie zostawiając żadnego śladu w liczniku.

### Instalacja

```bash
pip install cryptography pytest
python3 -m pytest tests/ -q      # 56/56
```

### GUI (`helix_pro_gui.py`)

Mini okno (tkinter, biblioteka standardowa) do szyfrowania/deszyfrowania
dowolnego pliku do dowolnego katalogu, bez linii komend:

```bash
python3 helix_pro_gui.py
```

Wybierasz plik źródłowy, tryb klucza (plik-klucz z możliwością
wygenerowania nowego, albo hasło) i klikasz Szyfruj/Deszyfruj — wtedy
wyskakuje natywne systemowe okno "Zapisz jako" (dowolny katalog, dowolna
nazwa), dokładnie jak w każdym innym programie.

Szyfrowanie zawsze zapisuje oryginalną nazwę pliku (a więc i rozszerzenie
— typ) WEWNĄTRZ zaszyfrowanej treści (`encrypt_file_with_name`). Dzięki
temu przy deszyfrowaniu GUI najpierw odczytuje odszyfrowaną treść do
pamięci, poznaje z niej prawdziwą oryginalną nazwę, i DOPIERO WTEDY
otwiera okno "Zapisz jako" z tą właściwą nazwą/rozszerzeniem podpowiedzianą
domyślnie — działa poprawnie nawet jeśli sam plik `.helixpro` został po
drodze przemianowany albo przesłany dalej (np. mailem). Pliki zaszyfrowane
starszą wersją tego GUI (bez zapisanej nazwy) nadal się odszyfrowują —
GUI wykrywa format automatycznie i w tym jednym przypadku prosi o nazwę
wynikową ręcznie.

Po każdej udanej operacji pola źródła i celu czyszczą się same — trzeba
świadomie wybrać plik od nowa przed kolejnym Szyfruj/Deszyfruj, żeby nie
dało się przypadkiem uruchomić operacji na nieaktualnych danych z
poprzedniego razu.

Przy szyfrowaniu jest checkbox "Kompresuj przed szyfrowaniem (gzip)"
(domyślnie zaznaczony) — status po zaszyfrowaniu pokazuje osiągnięty
współczynnik (rozmiar oryginału → rozmiar wyniku).

Drugi checkbox, "Śledź licznik odczytów", włącza `CounterLock` zamiast
zwykłego szyfrowania — dostępny tylko w trybie Plik-klucz (szary/odznaczony
w trybie Hasła, bo `CounterLock` go nie obsługuje). Przy szyfrowaniu z tą
opcją licznik startuje od 0. Przy deszyfrowaniu takiego pliku GUI najpierw
pokazuje ostrzeżenie, że **plik źródłowy zostanie nadpisany** nową wersją
z licznikiem +1 (sama treść się nie zmienia, ten sam klucz nadal działa) —
dopiero po potwierdzeniu pyta o katalog docelowy (nie o pełną nazwę pliku,
bo oryginalna nazwa jest odtwarzana automatycznie, tak jak w zwykłym
formacie "z nazwą"). Status po odszyfrowaniu pokazuje, jaki licznik był
przed operacją i jaki jest teraz w pliku źródłowym.

Logika poza samymi widgetami (nazywanie pliku, walidacja ścieżek, odczyt
klucza) jest w zwykłych funkcjach modułu, przetestowanych w
`tests/test_helix_pro_gui.py` niezależnie od GUI — samo okno wymaga
uruchomienia na Twoim komputerze, żeby je zobaczyć (środowisko, w
którym to powstało, nie ma wyświetlacza).

## Co zastąpiono i dlaczego

Audyt (2026-08) trzech oryginalnych modułów znalazł konkretne, nie
kosmetyczne problemy — każdy naprawiony w `helix_pro/`:

- **`HLX1.py` w ogóle nie szyfrował.** Mimo że opisywany jako moduł
  bezpieczeństwa z licznikiem odczytów, `encrypt_with_counter()` robił
  tylko `base64.b64encode(data)` — kodowanie, nie szyfrowanie. Każdy z
  dostępem do pliku czytał treść bez klucza. Podpis HMAC-SHA256 nad
  nagłówkiem był zrobiony poprawnie (stałoczasowe porównanie), ale
  chronił tylko licznik, nie treść. → `helix_pro.CounterLock`: treść
  faktycznie zaszyfrowana AES-256-GCM, licznik wpięty jako AAD w tę
  samą operację (kryptograficznie związany z ciphertextem).
- **`helix_cipher.py` używał klucza = `SHA256(hasło)`** bez soli i bez
  kosztu obliczeniowego (KDF) — podatne na brute-force/słownikowy atak
  offline i na tablice tęczowe. Do tego AES-CBC bez żadnej autentykacji
  — modyfikacja ciphertextu przechodzi bez wykrycia. →
  `helix_pro.derive_key_from_password()`: scrypt z losową solą
  (N=2¹⁴, r=8, p=1, jawnie udokumentowane), AES-256-GCM zamiast CBC.
- **`helix_lock_cipher.py` był już solidny** (prawdziwe AES-256-GCM),
  ale tylko w trybie pliku-klucza. `helix_pro` zachowuje to podejście i
  dokłada tryb hasła w tym samym, spójnym API.

Pełne uzasadnienie i zarchiwizowane pliki: `old/README.md`.

## Struktura

```
helix_pro/
    cipher.py         generate_key, derive_key_from_password,
                       encrypt_bytes/decrypt_bytes, encrypt_file/decrypt_file,
                       encrypt_file_with_name/decrypt_*_with_name, detect_format
    counter_lock.py    CounterLock (naprawiony licznik odczytów z HLX1) +
                       encrypt_file_with_counter/decrypt_file_with_counter
helix_pro_gui.py       mini GUI (tkinter) - szyfruj/deszyfruj dowolny plik
                       do dowolnego katalogu, opcjonalny licznik odczytów
tests/
    test_helix_pro.py      39 testów (cipher.py + counter_lock.py)
    test_helix_pro_gui.py  17 testów logiki GUI (bez wyświetlacza)
old/
    helix_cipher.py, helix_lock_cipher.py, HLX1.py   zarchiwizowane, nie używaj
    audyt.py           narzędzie do analizy entropii pliku - nadal działa,
                        osobne od szyfrowania, patrz old/README.md
    README.md          pełne uzasadnienie archiwizacji
```

## Ograniczenia (uczciwie)

To repozytorium nie jest audytowaną biblioteką kryptograficzną poziomu
produkcyjnego (np. TLS, Signal Protocol). `helix_pro` opiera się o
audytowaną bibliotekę `cryptography` (AES-256-GCM, scrypt), ale sam kod
integracyjny (formaty nagłówków, obsługa błędów) nie przeszedł
niezależnego audytu bezpieczeństwa. Dla realnie wysokiej stawki
(pieniądze, dane osobowe wrażliwe prawnie) użyj sprawdzonego,
audytowanego narzędzia end-to-end, nie tego repo. Zarządzanie kluczem
lub hasłem (bezpieczne przechowywanie, osobno od zaszyfrowanych danych)
jest zawsze Twoją odpowiedzialnością — żadne szyfrowanie tego nie
zastąpi.

## 🔗 Wszystkie modele i repozytoria

Pełna lista projektów: https://jbackk-lang.github.io

## Licencja

MIT — patrz `LICENSE`.
