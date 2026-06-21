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

**Funkcje:**
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
