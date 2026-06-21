# Helix‑Lock  
Warstwa ochronna świadomości i treści.  
Zamyka skręt, odcina szum, przepuszcza tylko kierunek.

Helix‑Lock to lekki szyfrator oparty na idei „skrętu helisy” —  
informacja przechodzi przez transformację, która ukrywa sens,  
a odsłania go tylko przy użyciu właściwego klucza.

---

## 🔐 Funkcje
- Szyfrowanie plików (tekstowych i binarnych)
- Odszyfrowywanie plików `.helix`
- Generowanie kluczy
- Minimalna zależność od bibliotek
- Prosta integracja z innymi narzędziami (np. audyt T₀/T₁/T₂)

---

## 📦 Instalacja
Wymagany Python 3.  
Repozytorium:  
https://github.com/jbackk-lang/Helix-Lock

---

## 🗝️ Generowanie klucza

```bash
python3 helix_lock_cipher.py keygen helix.key
