## 🔗 Wszystkie modele i repozytoria
Pełna lista projektów znajduje się na stronie:
https://jbackk-lang.github.io
---

# Helix‑Lock  
Warstwa ochronna świadomości i treści.  
Zamyka skręt, odcina szum, przepuszcza tylko kierunek.

Helix‑Lock to lekki szyfrator oparty na idei „skrętu helisy” —  
informacja przechodzi przez transformację, która ukrywa sens,  
a odsłania go tylko przy użyciu właściwego klucza.

---

# 📂 Zawartość repozytorium — co robi każdy program?

## **1. helix_cipher.py**
Podstawowy moduł szyfrujący.

**Funkcje:**
- szyfrowanie plików (tekstowych i binarnych),
- odszyfrowywanie plików `.helix`,
- prosta implementacja bez licznika odczytów.

To najlżejsza wersja szyfratora — dobra do integracji lub testów.

---

## **2. helix_lock_cipher.py**
Główna, „pełna” wersja szyfratora.

**Funkcje:**
- szyfrowanie i odszyfrowywanie plików z użyciem klucza,
- obsługa formatu `.helix`,
- zabezpieczenia integralności,
- możliwość rozszerzenia o licznik odczytów.

To wersja, której używasz na co dzień.

---

## **3. HLX1.py**
Implementacja szyfrowania **z licznikiem odczytań**.

**Funkcje:**
- zapisuje w nagłówku liczbę odszyfrowań (`counter`),
- przy każdym odczycie zwiększa licznik,
- podpisuje nagłówek HMAC, aby uniemożliwić manipulację,
- pozwala wykryć nieautoryzowane odczyty.

To moduł bezpieczeństwa — „czarna skrzynka” pliku.

---

## **4. audyt.py**
Narzędzie do analizy pliku po przejściach T₀ / T₁ / T₂.

python3 helix_lock_cipher.py encrypt dane.txt dane.helix helix.key

python3 helix_lock_cipher.py decrypt dane.helix dane.txt helix.key

python3 audyt.py plik.bin

**Funkcje:**Wynik:

T₀ — oryginał

T₁ — po pierwszym przejściu

T₂ — po drugim przejściu

ΔS — zmiana entropii

ΔC — zmiana korelacji

wniosek: „przeszedł / nie przeszedł transformację”
- wykonuje **dwa przejścia** (kompresja→dekompresja),
- mierzy entropię i rozkład bajtów,
- porównuje T₀ (oryginał), T₁ i T₂,
- wykrywa ślady transformacji.

Przydatne do sprawdzania, czy plik był modyfikowany lub przepuszczany przez obce narzędzia.

---

## **5. README.md**
Dokument, który właśnie czytasz.

---

# 🔐 Funkcje Helix‑Lock
- szyfrowanie plików (tekstowych i binarnych),
- odszyfrowywanie plików `.helix`,
- generowanie kluczy,
- integracja z licznikiem odczytów (HLX1),
- audyt przejść T₀/T₁/T₂.

---

# 📦 Instalacja
Wymagany Python 3.  
Repozytorium:  
https://github.com/jbackk-lang/Helix-Lock



---

# 🗝️ Generowanie klucza

```bash
python3 helix_lock_cipher.py keygen helix.key
```

---

# 🔧 Helix Pro — nowy moduł, co naprawiono (audyt)

`helix_pro/` to nowy, dodatkowy pakiet (nie zastępuje istniejących
plików — `helix_cipher.py`, `helix_lock_cipher.py`, `HLX1.py` działają
dalej bez zmian) powstały z audytu tego repo. Trzy konkretne rzeczy
zostały naprawione:

- **HLX1.py w ogóle nie szyfrował payloadu.** Mimo że README opisuje go
  jako moduł bezpieczeństwa, `encrypt_with_counter()` robił tylko
  `base64.b64encode(data)` — to kodowanie, nie szyfrowanie. Każdy z
  dostępem do pliku odczytał treść bez znajomości klucza. Sam podpis
  HMAC-SHA256 nad nagłówkiem+payloadem był zrobiony poprawnie
  (stałoczasowe porównanie), ale chronił tylko licznik przed manipulacją
  — nie treść przed odczytem. `helix_pro.counter_lock.CounterLock`
  robi to samo (licznik odczytów, ochrona przed cofnięciem), ale
  payload jest faktycznie zaszyfrowany AES-256-GCM, a licznik jest
  wpięty jako AAD w tę samą operację (kryptograficznie związany z
  ciphertextem, nie osobny podpis nad jawnym base64).
- **helix_cipher.py używał klucza = `SHA256(hasło)`** bez soli i bez
  kosztu obliczeniowego (KDF) — podatne na brute-force/słownikowy atak
  offline przy niezbyt losowym haśle, i na tablice tęczowe (ten sam
  hash zawsze dla tego samego hasła, niezależnie od pliku). Do tego
  AES-CBC bez żadnej autentykacji — modyfikacja ciphertextu przechodzi
  bez wykrycia (padding oracle / bit-flipping).
  `helix_pro.cipher.derive_key_from_password()` używa scrypt z losową
  solą (zapisywaną w nagłówku pliku) i jawnie udokumentowanym kosztem
  (N=2¹⁴, r=8, p=1).
- **helix_lock_cipher.py był już solidny** (prawdziwe AES-256-GCM z
  biblioteki `cryptography`) — Helix Pro nie zmienia tego podejścia,
  tylko rozszerza je o drugi tryb (hasło) w jednym spójnym API
  (`encrypt_file`/`decrypt_file` z `key=` albo `password=`), żeby nie
  trzeba było wybierać między "silne, ale tylko plik-klucz" a "wygodne
  hasło, ale słabe".

## Użycie

```python
from helix_pro import generate_key, encrypt_file, decrypt_file

key = generate_key()
encrypt_file("dane.txt", "dane.helixpro", key=key)
decrypt_file("dane.helixpro", "odzyskane.txt", key=key)

# albo trybem hasła (sól zapisana w nagłówku pliku, nie trzeba jej
# przechowywać osobno — ale samo hasło nadal musi być silne):
encrypt_file("dane.txt", "dane.helixpro", password="bardzo-dlugie-haslo")
decrypt_file("dane.helixpro", "odzyskane.txt", password="bardzo-dlugie-haslo")
```

Testy: `tests/test_helix_pro.py` — pierwsze testy w tym repo (18/18
przechodzi, zweryfikowane 2026-08-31), obejmują m.in. regresję wprost
przeciwko błędowi z HLX1.py (sprawdzenie, że zaszyfrowany blob nie
zawiera base64 oryginału), wykrywanie manipulacji ciphertextem/AAD/
licznikiem, oraz round-trip dla obu trybów.

**To repozytorium nadal nie jest audytowaną biblioteką kryptograficzną
poziomu produkcyjnego** (np. TLS, Signal Protocol) — `helix_pro` opiera
się o audytowaną bibliotekę `cryptography` (AES-256-GCM, scrypt), ale
sam kod integracyjny (formaty nagłówków, obsługa błędów) nie przeszedł
niezależnego audytu bezpieczeństwa. Dla realnie wysokiej stawki
(pieniądze, dane osobowe wrażliwe prawnie) użyj sprawdzonego,
audytowanego narzędzia end-to-end, nie tego repo.
