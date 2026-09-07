#!/usr/bin/env python3
"""
helix_pro_gui.py — mini GUI (tkinter, standardowa biblioteka) do
szyfrowania/deszyfrowania DOWOLNEGO pliku do DOWOLNEGO katalogu przez
helix_pro (AES-256-GCM). Nie ma tu żadnej osobnej logiki szyfrowania -
to tylko interfejs nad helix_pro/cipher.py.

Uruchomienie:
    pip install cryptography
    python3 helix_pro_gui.py

Zapis pliku wynikowego idzie przez natywne okno systemowe "Zapisz jako"
(filedialog.asksaveasfilename) - otwiera się automatycznie po kliknięciu
Szyfruj/Deszyfruj, jeśli plik wynikowy nie jest jeszcze ustawiony, więc
nie trzeba osobno klikać "Zapisz jako..." przed każdą operacją.

Logika bez-GUI (nazywanie pliku wynikowego, walidacja ścieżek,
rozstrzyganie klucz-vs-hasło) jest celowo wydzielona do zwykłych funkcji
na poziomie modułu (`suggest_output_name`, `validate_output_path`,
`resolve_key_kwargs`) - testowalnych bez uruchamiania GUI (patrz
tests/test_helix_pro_gui.py), bo środowisko, w którym to piszę, nie ma
wyświetlacza do uruchomienia prawdziwego okna Tk. Sama klasa `HelixProGUI`
(widgety, layout) nie jest tu testowana automatycznie - uruchom program
i przetestuj wizualnie na swoim komputerze.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helix_pro.cipher import (
    generate_key,
    encrypt_file_with_name,
    decrypt_bytes_with_name,
    decrypt_file,  # tylko jako fallback dla starego formatu (bez zapisanej nazwy)
    detect_format,
    HelixProError,
)
from helix_pro.counter_lock import encrypt_file_with_counter, decrypt_file_with_counter

ENCRYPTED_SUFFIX = ".helixpro"


# ---------------------------------------------------------------------
# Czysta logika (bez GUI) - testowalna bez wyświetlacza
# ---------------------------------------------------------------------

def suggest_output_name(source_path: str) -> str:
    """Nazwa pliku wynikowego proponowana po wybraniu pliku źródłowego:
    jeśli źródło wygląda na już zaszyfrowane (kończy się na .helixpro),
    proponuje deszyfrowanie (nazwa bez tego rozszerzenia); w przeciwnym
    razie proponuje szyfrowanie (dopisuje .helixpro). Zawsze tylko
    propozycja - użytkownik może wpisać cokolwiek innego w GUI."""
    base = os.path.basename(source_path)
    if base.lower().endswith(ENCRYPTED_SUFFIX):
        stripped = base[: -len(ENCRYPTED_SUFFIX)]
        return stripped if stripped else base + ".dec"
    return base + ENCRYPTED_SUFFIX


@dataclass
class PathValidationResult:
    ok: bool
    error: Optional[str] = None
    output_path: Optional[str] = None


def validate_output_path(source_path: str, output_path: str) -> PathValidationResult:
    """Sprawdza źródło i PEŁNĄ ścieżkę wynikową (wybraną natywnym oknem
    'Zapisz jako' - patrz _pick_output w GUI) - bez dotykania dysku poza
    sprawdzeniem istnienia (nic nie zapisuje). Nie decyduje o nadpisywaniu
    istniejącego pliku wynikowego - to GUI pyta użytkownika (potrzebuje
    messagebox, więc zostaje w klasie)."""
    if not source_path or not os.path.isfile(source_path):
        return PathValidationResult(False, "Wybierz istniejący plik źródłowy.")
    out_path = (output_path or "").strip()
    if not out_path:
        return PathValidationResult(False, "Wybierz miejsce zapisu pliku wynikowego (przycisk 'Zapisz jako...').")
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if not os.path.isdir(out_dir):
        return PathValidationResult(False, f"Katalog docelowy nie istnieje: {out_dir}")
    if os.path.abspath(out_path) == os.path.abspath(source_path):
        return PathValidationResult(False, "Plik wynikowy nie może być tym samym plikiem co źródłowy.")
    return PathValidationResult(True, output_path=out_path)


@dataclass
class KeyResolutionResult:
    ok: bool
    error: Optional[str] = None
    kwargs: Optional[dict] = None  # {"key": bytes} albo {"password": str}


def resolve_key_kwargs(mode: str, key_path: str, password: str) -> KeyResolutionResult:
    """Zamienia wybór trybu (GUI: radiobutton) na kwargs dla
    encrypt_file()/decrypt_file(). Czyta plik klucza z dysku (jedyne
    I/O w tej funkcji) - reszta to walidacja."""
    if mode == "key":
        if not key_path or not os.path.isfile(key_path):
            return KeyResolutionResult(False, "Wybierz istniejący plik klucza (albo wygeneruj nowy).")
        try:
            with open(key_path, "rb") as f:
                key = f.read()
        except OSError as exc:
            return KeyResolutionResult(False, f"Nie udało się odczytać pliku klucza: {exc}")
        if len(key) != 32:
            return KeyResolutionResult(False, f"Plik klucza ma {len(key)} bajtów, oczekiwano 32 - to nie jest poprawny klucz Helix Pro.")
        return KeyResolutionResult(True, kwargs={"key": key})
    elif mode == "password":
        if not password:
            return KeyResolutionResult(False, "Podaj hasło.")
        return KeyResolutionResult(True, kwargs={"password": password})
    else:
        return KeyResolutionResult(False, f"Nieznany tryb: {mode!r}")


# ---------------------------------------------------------------------
# GUI (tkinter) - cienka warstwa nad powyższą logiką + helix_pro
# ---------------------------------------------------------------------

def _build_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    class HelixProGUI(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Helix Pro — szyfrowanie plików")
            self.geometry("620x480")
            self.minsize(560, 440)

            self.source_path = tk.StringVar()
            self.output_path = tk.StringVar()
            self.mode = tk.StringVar(value="key")
            self.key_path = tk.StringVar()
            self.password = tk.StringVar()
            self.show_password = tk.BooleanVar(value=False)
            self.compress = tk.BooleanVar(value=True)
            self.use_counter = tk.BooleanVar(value=False)

            self._build_ui()

        def _build_ui(self):
            pad = {"padx": 10, "pady": 6}

            frame_src = ttk.LabelFrame(self, text="1. Plik źródłowy (dowolny plik, dowolny typ)")
            frame_src.pack(fill="x", **pad)
            ttk.Entry(frame_src, textvariable=self.source_path).pack(side="left", fill="x", expand=True, padx=6, pady=6)
            ttk.Button(frame_src, text="Wybierz plik...", command=self._pick_source).pack(side="left", padx=6)

            frame_dst = ttk.LabelFrame(self, text="2. Plik wynikowy (dowolny katalog, dowolna nazwa)")
            frame_dst.pack(fill="x", **pad)
            ttk.Entry(frame_dst, textvariable=self.output_path).pack(side="left", fill="x", expand=True, padx=6, pady=6)
            ttk.Button(frame_dst, text="Zapisz jako...", command=self._pick_output).pack(side="left", padx=6)

            frame_mode = ttk.LabelFrame(self, text="3. Klucz")
            frame_mode.pack(fill="x", **pad)
            row_mode = ttk.Frame(frame_mode); row_mode.pack(fill="x", padx=6, pady=4)
            ttk.Radiobutton(row_mode, text="Plik-klucz", variable=self.mode, value="key",
                             command=self._refresh_mode).pack(side="left")
            ttk.Radiobutton(row_mode, text="Hasło", variable=self.mode, value="password",
                             command=self._refresh_mode).pack(side="left", padx=20)

            self.key_frame = ttk.Frame(frame_mode)
            ttk.Entry(self.key_frame, textvariable=self.key_path).pack(side="left", fill="x", expand=True, padx=(6, 6))
            ttk.Button(self.key_frame, text="Wybierz klucz...", command=self._pick_key).pack(side="left")
            ttk.Button(self.key_frame, text="Generuj nowy...", command=self._generate_key).pack(side="left", padx=6)

            self.password_frame = ttk.Frame(frame_mode)
            self.password_entry = ttk.Entry(self.password_frame, textvariable=self.password, show="*")
            self.password_entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
            ttk.Checkbutton(self.password_frame, text="pokaż", variable=self.show_password,
                             command=self._toggle_password).pack(side="left")

            frame_compress = ttk.Frame(self)
            frame_compress.pack(fill="x", padx=10)
            ttk.Checkbutton(
                frame_compress,
                text="Kompresuj przed szyfrowaniem (gzip) — tylko przy szyfrowaniu; "
                     "pomijany automatycznie, gdyby powiększał plik",
                variable=self.compress,
            ).pack(side="left")

            frame_counter = ttk.Frame(self)
            frame_counter.pack(fill="x", padx=10, pady=(4, 0))
            self.counter_check = ttk.Checkbutton(
                frame_counter,
                text="Śledź licznik odczytów (tylko tryb Plik-klucz) — przy szyfrowaniu "
                     "startuje od 0; każde odszyfrowanie NADPISUJE plik źródłowy nową "
                     "wersją z licznikiem +1",
                variable=self.use_counter,
            )
            self.counter_check.pack(side="left")

            self._refresh_mode()  # po zbudowaniu counter_check, ktory ta metoda wlacza/wylacza

            frame_actions = ttk.Frame(self)
            frame_actions.pack(fill="x", **pad)
            ttk.Button(frame_actions, text="🔒 Szyfruj", command=self._encrypt).pack(side="left", padx=6, expand=True, fill="x")
            ttk.Button(frame_actions, text="🔓 Deszyfruj", command=self._decrypt).pack(side="left", padx=6, expand=True, fill="x")

            frame_status = ttk.LabelFrame(self, text="Status")
            frame_status.pack(fill="both", expand=True, **pad)
            self.status_text = tk.Text(frame_status, height=8, wrap="word", state="disabled")
            self.status_text.pack(fill="both", expand=True, padx=6, pady=6)

        def _refresh_mode(self):
            if self.mode.get() == "key":
                self.password_frame.pack_forget()
                self.key_frame.pack(fill="x", padx=6, pady=4)
                self.counter_check.state(["!disabled"])
            else:
                self.key_frame.pack_forget()
                self.password_frame.pack(fill="x", padx=6, pady=4)
                # CounterLock nie ma trybu hasla (patrz counter_lock.py) -
                # wylaczamy i odznaczamy checkbox, zeby nie dalo sie wybrac
                # kombinacji, ktora i tak zostalaby odrzucona w _encrypt/_decrypt.
                self.use_counter.set(False)
                self.counter_check.state(["disabled"])

        def _toggle_password(self):
            self.password_entry.config(show="" if self.show_password.get() else "*")

        def _pick_source(self):
            path = filedialog.askopenfilename(title="Wybierz plik źródłowy")
            if path:
                self.source_path.set(path)
                self.output_path.set("")  # nowe zrodlo -> stara propozycja pliku wynikowego juz nieaktualna

        def _pick_output(self) -> bool:
            """Otwiera natywne okno 'Zapisz jako' (dowolny katalog, dowolna
            nazwa) - podpowiada katalog i nazwę na podstawie źródła, jeśli
            jest wybrane. Zwraca True, jeśli użytkownik coś wybrał (nie
            anulował), żeby _run_operation wiedziało, czy kontynuować."""
            src = self.source_path.get()
            kwargs = {"title": "Zapisz jako"}
            if src:
                kwargs["initialdir"] = os.path.dirname(src)
                kwargs["initialfile"] = suggest_output_name(src)
            path = filedialog.asksaveasfilename(**kwargs)
            if path:
                self.output_path.set(path)
                return True
            return False

        def _pick_key(self):
            path = filedialog.askopenfilename(title="Wybierz plik klucza")
            if path:
                self.key_path.set(path)

        def _generate_key(self):
            path = filedialog.asksaveasfilename(
                title="Zapisz nowy plik klucza", defaultextension=".key", initialfile="helix.key"
            )
            if not path:
                return
            key = generate_key()
            with open(path, "wb") as f:
                f.write(key)
            self.key_path.set(path)
            self.mode.set("key")
            self._refresh_mode()
            self._log(
                f"Wygenerowano nowy klucz: {path}\n"
                "Pilnuj go osobno od zaszyfrowanych plików — bez niego nic nie odszyfrujesz."
            )

        def _log(self, msg: str):
            self.status_text.config(state="normal")
            self.status_text.insert("end", msg + "\n\n")
            self.status_text.see("end")
            self.status_text.config(state="disabled")

        def _reset_after_action(self):
            """Po udanej operacji czyścimy źródło i cel, żeby przy
            następnym kliknięciu Szyfruj/Deszyfruj trzeba było świadomie
            wybrać plik od nowa - zapobiega przypadkowemu użyciu
            nieaktualnych danych z poprzedniej operacji (np. deszyfrowaniu
            tego samego pliku, który przed chwilą zaszyfrowano, bez
            zmiany pola źródła)."""
            self.source_path.set("")
            self.output_path.set("")

        def _encrypt(self):
            if not self.source_path.get() or not os.path.isfile(self.source_path.get()):
                messagebox.showerror("Błąd", "Wybierz istniejący plik źródłowy.")
                return

            # Jesli plik wynikowy nie jest jeszcze ustawiony, okno "Zapisz
            # jako" wyskakuje TERAZ, od razu po kliknieciu - a nie tylko
            # na zadanie osobnym przyciskiem, ktory latwo pominac.
            if not self.output_path.get():
                if not self._pick_output():
                    return  # uzytkownik anulowal okno zapisu

            validation = validate_output_path(self.source_path.get(), self.output_path.get())
            if not validation.ok:
                messagebox.showerror("Błąd", validation.error)
                return
            out_path = validation.output_path
            if os.path.exists(out_path):
                if not messagebox.askyesno("Plik istnieje", f"{out_path}\njuż istnieje. Nadpisać?"):
                    return

            key_result = resolve_key_kwargs(self.mode.get(), self.key_path.get(), self.password.get())
            if not key_result.ok:
                messagebox.showerror("Błąd", key_result.error)
                return

            with_counter = self.use_counter.get() and self.mode.get() == "key"

            src_size = os.path.getsize(self.source_path.get())
            try:
                if with_counter:
                    # CounterLock zamiast zwyklego encrypt_bytes - licznik
                    # (start od 0) jest wpiety jako AAD. Nazwa+kompresja
                    # pakowane tym samym pack_named_payload() co ponizej,
                    # wiec typ pliku odtwarza sie tak samo przy odszyfrowaniu.
                    encrypt_file_with_counter(
                        self.source_path.get(), out_path, compress=self.compress.get(), **key_result.kwargs
                    )
                else:
                    # _with_name: oryginalna nazwa (a wiec i rozszerzenie/typ)
                    # trafia do wnetrza zaszyfrowanej tresci, wiec deszyfrowanie
                    # odtworzy ja poprawnie nawet jesli ten plik .helixpro
                    # zostanie potem przemianowany/przeslany dalej. compress=
                    # gzip "smart" - uzyty tylko jesli faktycznie cos zmniejsza.
                    encrypt_file_with_name(
                        self.source_path.get(), out_path, compress=self.compress.get(), **key_result.kwargs
                    )
                out_size = os.path.getsize(out_path)
                ratio_note = ""
                if self.compress.get() and src_size > 0:
                    ratio_note = f" (kompresja: {src_size} B → {out_size} B, {out_size / src_size:.0%} oryginału)"
                counter_note = " [z licznikiem odczytów, start=0]" if with_counter else ""
                self._log(f"Zaszyfrowano{ratio_note}{counter_note}:\n{self.source_path.get()}\n→ {out_path}")
                self._reset_after_action()
            except HelixProError as exc:
                messagebox.showerror("Błąd — szyfrowanie", str(exc))
                self._log(f"BŁĄD (szyfrowanie): {exc}")
            except OSError as exc:
                messagebox.showerror("Błąd pliku", str(exc))
                self._log(f"BŁĄD (szyfrowanie): {exc}")

        def _decrypt(self):
            src = self.source_path.get()
            if not src or not os.path.isfile(src):
                messagebox.showerror("Błąd", "Wybierz istniejący plik źródłowy.")
                return

            fmt = detect_format(src)
            if fmt == "unknown":
                messagebox.showerror(
                    "Błąd",
                    f"Nierozpoznany format pliku:\n{src}\nTo nie jest plik zaszyfrowany przez Helix Pro.",
                )
                return

            key_result = resolve_key_kwargs(self.mode.get(), self.key_path.get(), self.password.get())
            if not key_result.ok:
                messagebox.showerror("Błąd", key_result.error)
                return

            if fmt == "counter":
                if self.mode.get() != "key":
                    messagebox.showerror(
                        "Błąd",
                        "Ten plik ma licznik odczytów (CounterLock) - obsługiwany tylko "
                        "w trybie Plik-klucz, nie w trybie Hasła.",
                    )
                    return
                self._decrypt_counter(src, key_result.kwargs)
            elif fmt == "named":
                self._decrypt_named(src, key_result.kwargs)
            else:  # "plain" - stary format sprzed 2026-08, bez zapisanej nazwy w srodku
                self._decrypt_plain(src, key_result.kwargs)

        def _decrypt_named(self, src: str, key_kwargs: dict):
            """Deszyfruje najpierw DO PAMIĘCI, żeby poznać oryginalną
            nazwę/rozszerzenie ZANIM zapyta o miejsce zapisu - dzięki temu
            okno 'Zapisz jako' od razu podpowiada właściwy typ pliku,
            niezależnie od tego, jak nazywał się plik .helixpro."""
            try:
                original_name, content = decrypt_bytes_with_name(src, **key_kwargs)
            except HelixProError as exc:
                messagebox.showerror("Błąd — deszyfrowanie", str(exc))
                self._log(f"BŁĄD (deszyfrowanie): {exc}")
                return
            except OSError as exc:
                messagebox.showerror("Błąd pliku", str(exc))
                self._log(f"BŁĄD (deszyfrowanie): {exc}")
                return

            save_kwargs = {"title": "Zapisz jako", "initialfile": original_name}
            ext = os.path.splitext(original_name)[1]
            if ext:
                save_kwargs["defaultextension"] = ext
            out_path = filedialog.asksaveasfilename(**save_kwargs)
            if not out_path:
                return  # anulowano - nic nie zapisane na dysku
            if os.path.exists(out_path):
                if not messagebox.askyesno("Plik istnieje", f"{out_path}\njuż istnieje. Nadpisać?"):
                    return

            try:
                with open(out_path, "wb") as f:
                    f.write(content)
            except OSError as exc:
                messagebox.showerror("Błąd pliku", str(exc))
                self._log(f"BŁĄD (deszyfrowanie): {exc}")
                return

            self._log(f"Odszyfrowano (nazwa i typ odtworzone automatycznie: '{original_name}'):\n{src}\n→ {out_path}")
            self._reset_after_action()

        def _decrypt_counter(self, src: str, key_kwargs: dict):
            """Deszyfruje plik z licznikiem odczytów (CounterLock). W
            odróżnieniu od _decrypt_named/_decrypt_plain, plik WYNIKOWY
            zawsze idzie do wskazanego KATALOGU pod odtworzoną nazwą
            (decrypt_file_with_counter samo ją odtwarza) - i, co ważne,
            plik ŹRÓDŁOWY (src) zostaje przy tym NADPISANY nową wersją z
            licznikiem +1, więc pytamy o potwierdzenie zanim cokolwiek
            zrobimy."""
            if not messagebox.askyesno(
                "Licznik odczytów — uwaga",
                f"{src}\n\nTen plik ma włączony licznik odczytów. Odszyfrowanie go "
                "NADPISZE ten plik nową wersją z licznikiem zwiększonym o 1 "
                "(sama zaszyfrowana treść się nie zmienia - to samo hasło/klucz "
                "nadal działa). Kontynuować?",
            ):
                return

            out_dir = filedialog.askdirectory(title="Wybierz katalog docelowy")
            if not out_dir:
                return  # anulowano - nic nie zapisane, plik zrodlowy NIE zostal ruszony

            try:
                out_path, counter_before = decrypt_file_with_counter(src, out_dir, **key_kwargs)
            except HelixProError as exc:
                messagebox.showerror("Błąd — deszyfrowanie", str(exc))
                self._log(f"BŁĄD (deszyfrowanie z licznikiem): {exc}")
                return
            except OSError as exc:
                messagebox.showerror("Błąd pliku", str(exc))
                self._log(f"BŁĄD (deszyfrowanie z licznikiem): {exc}")
                return

            self._log(
                f"Odszyfrowano (licznik odczytów: był {counter_before}, plik źródłowy "
                f"zapisany teraz z licznikiem {counter_before + 1}):\n{src}\n→ {out_path}"
            )
            self._reset_after_action()

        def _decrypt_plain(self, src: str, key_kwargs: dict):
            """Fallback dla plikow .helixpro zaszyfrowanych starym
            encrypt_file() (sprzed dodania zapisywanej nazwy) - nazwa
            wynikowa jest tylko PROPOZYCJA (suggest_output_name), bo w
            tym formacie nie ma skad odtworzyc oryginalnej."""
            if not self.output_path.get():
                if not self._pick_output():
                    return

            validation = validate_output_path(src, self.output_path.get())
            if not validation.ok:
                messagebox.showerror("Błąd", validation.error)
                return
            out_path = validation.output_path
            if os.path.exists(out_path):
                if not messagebox.askyesno("Plik istnieje", f"{out_path}\njuż istnieje. Nadpisać?"):
                    return

            try:
                decrypt_file(src, out_path, **key_kwargs)
                self._log(
                    f"Odszyfrowano (stary format bez zapisanej nazwy - sprawdź rozszerzenie ręcznie):\n{src}\n→ {out_path}"
                )
                self._reset_after_action()
            except HelixProError as exc:
                messagebox.showerror("Błąd — deszyfrowanie", str(exc))
                self._log(f"BŁĄD (deszyfrowanie): {exc}")
            except OSError as exc:
                messagebox.showerror("Błąd pliku", str(exc))
                self._log(f"BŁĄD (deszyfrowanie): {exc}")

    return HelixProGUI


def main():
    HelixProGUI = _build_gui()
    app = HelixProGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
