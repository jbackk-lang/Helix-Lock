# Helix-Lock

Helix‑Lock — warstwa ochronna świadomości i treści.

Zamyka skręt, odcina szum, przepuszcza tylko kierunek.

Szyfruje pliki — szyfruje dostęp do sensu.

### Szyfrowanie pliku
python3 helix_cipher.py encrypt <plik> <haslo>

### Odszyfrowanie pliku
python3 helix_cipher.py decrypt <plik.helix> <haslo>

### Z kluczem

Generowanie klucza: python helix_lock_cipher.py keygen helix.key

Szyfrowanie: python helix_lock_cipher.py encrypt secret.txt secret.helix helix.key

Odszyfrowanie: python helix_lock_cipher.py decrypt secret.helix secret.txt helix.key
