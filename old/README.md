# old/ — poprzednie moduły (zarchiwizowane)

Te cztery pliki (`helix_cipher.py`, `helix_lock_cipher.py`, `HLX1.py`,
`audyt.py`) to oryginalna, pierwsza wersja tego repo, przeniesiona tu
2026-08 żeby nie mieszała się z aktualną wersją (`helix_pro/`, patrz
główny README.md). Zostają tu jako historia i punkt odniesienia —
nie usunięte, ale też nie są już zalecaną drogą.

**Nie używaj tych plików do niczego nowego.** Konkretne powody, każdy
naprawiony w `helix_pro/`:

- **`HLX1.py`** — mimo nazwy ("licznik odczytów", opisywany wcześniej
  jako moduł bezpieczeństwa) **w ogóle nie szyfrował** treści.
  `encrypt_with_counter()` robił tylko `base64.b64encode(data)` — to
  kodowanie, nie szyfrowanie. Każdy z dostępem do pliku czytał treść
  bez klucza. Sam podpis HMAC-SHA256 nad nagłówkiem był poprawny, ale
  chronił tylko licznik, nie treść. Zamiennik: `helix_pro.CounterLock`.
- **`helix_cipher.py`** — klucz to goły `SHA256(hasło)`, bez soli i bez
  kosztu obliczeniowego (KDF) — podatne na brute-force/słownikowy atak
  offline. Do tego AES-CBC bez żadnej autentykacji (modyfikacja
  ciphertextu przechodzi niezauważona). Zamiennik:
  `helix_pro.derive_key_from_password()` (scrypt + sól) w połączeniu z
  `encrypt_file()`.
- **`helix_lock_cipher.py`** — ten był już solidny (prawdziwe AES-256-GCM),
  ale tylko w trybie pliku-klucza, bez trybu hasła. Zamiennik:
  `helix_pro.encrypt_file()`/`decrypt_file()`, oba tryby w jednym API.
- **`audyt.py`** — narzędzie do analizy entropii/korelacji po przejściu
  zlib, niezwiązane bezpośrednio z szyfrowaniem — zostaje tu jako
  osobne, wciąż działające narzędzie diagnostyczne (`python3 old/audyt.py plik.bin`),
  nie ma odpowiednika w `helix_pro/`, bo robi coś innego (analiza, nie
  szyfrowanie).

Pełny audyt i uzasadnienie każdej naprawy: `../README.md` sekcja
"Co zastąpiono i dlaczego".
