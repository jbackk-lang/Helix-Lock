#!/usr/bin/env python3
"""Helix-Lock — one lightweight Tk desktop app for Windows, macOS and Linux."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from helix_pro.airp_identity import AIRPIdentityManager
from helix_pro.airp_key_fingerprint import (
    KeyFingerprint, create_key_fingerprint, representation_fingerprint_file,
    verify_key_fingerprint,
)
from helix_pro.airp_http_anchor import HTTPTrustAnchor
from helix_pro.airp_ledger import AIRPIntegrityLedger
from helix_pro.airp_quorum import QuorumTrustAnchor
from helix_pro.cipher import (
    HelixProError, decrypt_bytes_with_name, decrypt_file, detect_format,
    encrypt_file_with_name, generate_key,
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEDGER = os.path.join(os.path.expanduser("~"), ".helix_lock", "identity.sqlite3")
BG, PANEL, ACCENT, FG, MUTED = "#101827", "#182437", "#54D6A0", "#F2F6FC", "#9FB0C5"


class HelixLockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Helix-Lock")
        self.geometry("820x690")
        self.minsize(700, 610)
        self.configure(bg=BG)
        self.source = tk.StringVar()
        self.key_file = tk.StringVar()
        self.password = tk.StringVar()
        self.mode = tk.StringVar(value="key")
        self.object_id = tk.StringVar(value="my-object")
        self.key_id = tk.StringVar(value="key-v1")
        self.old_key_id = tk.StringVar(value="key-v0")
        self.old_key_file = tk.StringVar()
        self.signer_file = tk.StringVar()
        self.signer_password = tk.StringVar()
        self.ledger_path = tk.StringVar(value=DEFAULT_LEDGER)
        self.anchor_text = tk.StringVar()
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=PANEL, foreground=FG)
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED)
        style.configure("TButton", padding=(12, 8), font=("Segoe UI", 10))
        style.configure("Accent.TButton", background=ACCENT, foreground="#10202A", padding=(12, 9), font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#24344B", foreground=FG, insertcolor=FG)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 10), background=PANEL, foreground=FG)
        style.map("TNotebook.Tab", background=[("selected", "#263B52")])

    def _build(self):
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=22, pady=(18, 12))
        self._logo(head)
        tk.Label(head, text="HELIX-LOCK", bg=BG, fg=FG, font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=(78, 0), pady=(4, 0))
        tk.Label(head, text="Szyfrowanie plików  ·  Tożsamość kluczy  ·  Zaufanie AIRP", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=(80, 0))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.dashboard_tab = ttk.Frame(self.tabs); self.tabs.add(self.dashboard_tab, text="Przegląd bezpieczeństwa")
        self.file_tab = ttk.Frame(self.tabs); self.tabs.add(self.file_tab, text="Pliki")
        self.fp_tab = ttk.Frame(self.tabs); self.tabs.add(self.fp_tab, text="Odcisk klucza")
        self.trust_tab = ttk.Frame(self.tabs); self.tabs.add(self.trust_tab, text="AIRP / Quorum")
        self._build_dashboard()
        self._build_files()
        self._build_fingerprint()
        self._build_trust()
        self.status = tk.StringVar(value="Gotowy. Klucze pozostają lokalnie na Twoim urządzeniu.")
        self.refresh_dashboard()
        bar = tk.Frame(self, bg="#0C1421"); bar.pack(fill="x", side="bottom")
        tk.Label(bar, textvariable=self.status, bg="#0C1421", fg=MUTED, anchor="w", padx=16, pady=10).pack(fill="x")

    def _logo(self, parent):
        c = tk.Canvas(parent, width=66, height=66, bg=BG, highlightthickness=0)
        c.place(x=0, y=0)
        c.create_oval(7, 7, 59, 59, outline=ACCENT, width=2)
        c.create_oval(18, 18, 48, 48, outline="#8BC8FF", width=2)
        c.create_line(33, 33, 33, 61, fill=ACCENT, width=3)

    def _section(self, parent, title, subtitle):
        box = tk.Frame(parent, bg=PANEL, highlightbackground="#2A3B53", highlightthickness=1)
        box.pack(fill="x", padx=14, pady=8)
        tk.Label(box, text=title, bg=PANEL, fg=FG, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
        tk.Label(box, text=subtitle, bg=PANEL, fg=MUTED, font=("Segoe UI", 9), wraplength=710, justify="left").pack(anchor="w", padx=14, pady=(0, 10))
        return box

    def _entry(self, parent, label, variable, *, secret=False, browse=None):
        row = tk.Frame(parent, bg=PANEL); row.pack(fill="x", padx=14, pady=4)
        tk.Label(row, text=label, bg=PANEL, fg=MUTED, width=17, anchor="w").pack(side="left")
        entry = ttk.Entry(row, textvariable=variable, show="*" if secret else "")
        entry.pack(side="left", fill="x", expand=True, padx=6)
        if browse:
            ttk.Button(row, text="Wybierz…", command=browse).pack(side="left")
        return entry


    def _metric(self, parent, title, value, note):
        card = tk.Frame(parent, bg=PANEL, highlightbackground="#2A3B53", highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(card, textvariable=value, bg=PANEL, fg=ACCENT, font=("Segoe UI", 19, "bold")).pack(anchor="w", padx=12)
        tk.Label(card, text=note, bg=PANEL, fg=MUTED, font=("Segoe UI", 8), wraplength=210, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

    def _build_dashboard(self):
        intro = self._section(self.dashboard_tab, "CENTRUM BEZPIECZENSTWA", "Podglad lokalnego rejestru AIRP i wybranego pliku. Brak danych nie oznacza pozytywnego wyniku kontroli.")
        ttk.Button(intro, text="Odswiez podglad", command=self.refresh_dashboard).pack(anchor="e", padx=14, pady=(0, 10))
        row1 = tk.Frame(self.dashboard_tab, bg=BG); row1.pack(fill="x", padx=10)
        row2 = tk.Frame(self.dashboard_tab, bg=BG); row2.pack(fill="x", padx=10)
        self.dash_chain = tk.StringVar(value="—")
        self.dash_sequence = tk.StringVar(value="—")
        self.dash_anchor = tk.StringVar(value="NIEZNANY")
        self.dash_counter = tk.StringVar(value="—")
        self.dash_file = tk.StringVar(value="Nie wybrano")
        self.dash_events = tk.StringVar(value="—")
        self._metric(row1, "LANCUCH AIRP", self.dash_chain, "Dane lokalne; nie oznaczaja potwierdzenia quorum.")
        self._metric(row1, "SEKWENCJA", self.dash_sequence, "Liczba zdarzen w lokalnym dzienniku.")
        self._metric(row1, "CHECKPOINT", self.dash_anchor, "Stan zewnetrznego anchor wymaga osobnej weryfikacji.")
        self._metric(row2, "LICZNIK COUNTERLOCK", self.dash_counter, "Ostatni licznik zapisany w lokalnym dzienniku AIRP.")
        self._metric(row2, "FORMAT PLIKU", self.dash_file, "Rozpoznanie naglowka, nie weryfikacja kluczem.")
        self._metric(row2, "ZDARZENIA", self.dash_events, "Liczba wpisow w dzienniku AIRP.")
        history = self._section(self.dashboard_tab, "OS CZASU ZDARZEN", "Ostatnie wpisy AIRP; bez kluczy, hasel i tresci plikow.")
        self.dash_history = tk.Text(history, height=9, bg="#0C1421", fg=FG, insertbackground=FG, relief="flat", wrap="word", font=("Consolas", 9), state="disabled")
        self.dash_history.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        tk.Label(self.dashboard_tab, text="WAZNE: lokalna baza SQLite sama nie chroni przed cofaniem calej bazy. Ochrona przed rollbackiem wymaga niezaleznego Trust Anchor / quorum.", bg=BG, fg="#F2C879", font=("Segoe UI", 9), wraplength=730, justify="left").pack(fill="x", padx=18, pady=(4, 8))

    def refresh_dashboard(self):
        self.dash_file.set("Nie wybrano")
        selected = self.source.get().strip() if hasattr(self, "source") else ""
        if selected and os.path.isfile(selected):
            try:
                with open(selected, "rb") as stream:
                    header = stream.read(13)
                magic = header[:4]
                if magic == b"HLXC" and len(header) == 13 and header[4] == 1:
                    file_counter = struct.unpack(">Q", header[5:13])[0]
                    self.dash_file.set("CounterLock / HLXC")
                    self.dash_counter.set(str(file_counter) + " (naglowek; niezweryfikowany)")
                elif magic == b"HLXN":
                    self.dash_file.set("Helix named / HLXN")
                elif magic == b"HLXP":
                    self.dash_file.set("Helix / HLXP")
                else:
                    self.dash_file.set("Nieznany / zwykly")
            except OSError:
                self.dash_file.set("Nie mozna odczytac")
        else:
            self.dash_counter.set("—")

        db_path = self.ledger_path.get().strip() if hasattr(self, "ledger_path") else DEFAULT_LEDGER
        self.dash_chain.set("BRAK BAZY")
        self.dash_sequence.set("—")
        self.dash_anchor.set("NIE SPRAWDZONO")
        self.dash_events.set("—")
        history_lines = ["Brak lokalnej bazy AIRP. Zarejestruj klucz w zakladce AIRP / Quorum."]
        if db_path and os.path.isfile(db_path):
            try:
                uri = "file:" + quote(os.path.abspath(db_path).replace(os.sep, "/")) + "?mode=ro"
                with sqlite3.connect(uri, uri=True, timeout=2) as db:
                    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    if "airp_ledger_events" in tables:
                        all_rows = db.execute("SELECT sequence,timestamp_utc,event_type,object_id,payload_json,previous_hash,event_hash FROM airp_ledger_events ORDER BY sequence").fetchall()
                        total = len(all_rows)
                        self.dash_events.set(str(total))
                        self.dash_sequence.set(str(total))
                        expected_sequence = 1
                        previous_hash = "0" * 64
                        chain_valid = True
                        for seq, stamp, event_type, object_id, payload_json, stored_previous, stored_hash in all_rows:
                            payload = json.loads(payload_json)
                            material = {"sequence": seq, "timestamp_utc": stamp, "event_type": event_type, "object_id": object_id, "payload": payload, "previous_hash": stored_previous}
                            canonical = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                            calculated_hash = hashlib.sha256(canonical).hexdigest()
                            if seq != expected_sequence or stored_previous != previous_hash or calculated_hash != stored_hash:
                                chain_valid = False
                                break
                            expected_sequence += 1
                            previous_hash = stored_hash
                        self.dash_chain.set("CHAIN OK" if chain_valid else "CHAIN BLEDNY")
                        latest_counter = None
                        history_lines = []
                        for seq, stamp, event_type, object_id, payload_json, stored_previous, stored_hash in reversed(all_rows[-8:]):
                            payload = json.loads(payload_json)
                            if event_type == "counter_observed" and latest_counter is None:
                                latest_counter = payload.get("counter")
                            history_lines.append("#%s  %s  %s  [%s]" % (seq, stamp, event_type, object_id))
                        if latest_counter is not None:
                            self.dash_counter.set(str(latest_counter))
                        elif self.dash_file.get() != "CounterLock / HLXC":
                            self.dash_counter.set("BRAK WPISOW")
                        if not history_lines:
                            history_lines = ["Dziennik jest pusty."]
                        history_lines.extend(["", "Uwaga: lokalny odczyt nie potwierdza stanu zewnetrznego quorum."])
                    else:
                        history_lines = ["Wybrana baza nie zawiera tabeli dziennika AIRP."]
            except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
                self.dash_chain.set("BLAD ODCZYTU")
                history_lines = ["Nie udalo sie odczytac bazy AIRP: " + str(exc)]
        self.dash_history.configure(state="normal")
        self.dash_history.delete("1.0", "end")
        self.dash_history.insert("1.0", "\\n".join(history_lines))
        self.dash_history.configure(state="disabled")

    def _build_files(self):
        card = self._section(self.file_tab, "01  Szyfruj / odszyfruj", "Wybierz plik, sposób uwierzytelnienia i jedną operację. Program sam podpowie nazwę pliku wynikowego.")
        self._entry(card, "Plik źródłowy", self.source, browse=self._pick_source)
        row = tk.Frame(card, bg=PANEL); row.pack(fill="x", padx=14, pady=7)
        ttk.Radiobutton(row, text="Plik-klucz (zalecane)", variable=self.mode, value="key", command=self._refresh_mode).pack(side="left")
        ttk.Radiobutton(row, text="Hasło", variable=self.mode, value="password", command=self._refresh_mode).pack(side="left", padx=18)
        self.key_row = tk.Frame(card, bg=PANEL); self.key_row.pack(fill="x")
        self._entry(self.key_row, "Plik klucza", self.key_file, browse=self._pick_key)
        ttk.Button(card, text="Wygeneruj nowy klucz…", command=self._generate_key).pack(anchor="e", padx=14, pady=5)
        self.pass_row = tk.Frame(card, bg=PANEL)
        self._entry(self.pass_row, "Hasło", self.password, secret=True)
        actions = tk.Frame(card, bg=PANEL); actions.pack(fill="x", padx=14, pady=(12, 14))
        ttk.Button(actions, text="🔒  Szyfruj", style="Accent.TButton", command=self._encrypt).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(actions, text="🔓  Odszyfruj", command=self._decrypt).pack(side="left", expand=True, fill="x", padx=(6, 0))
        self._refresh_mode()
        note = self._section(self.file_tab, "Ważne", "Zachowaj kopię klucza poza komputerem z zaszyfrowanymi danymi. Bez klucza lub hasła odzyskanie treści nie będzie możliwe. Odcisk klucza nie zastępuje klucza.")

    def _build_fingerprint(self):
        card = self._section(self.fp_tab, "02  Tożsamość klucza", "Utwórz odcisk powiązany z identyfikatorem obiektu i klucza. Manifest nie zawiera klucza ani hasła.")
        self._entry(card, "Plik klucza", self.key_file, browse=self._pick_key)
        self._entry(card, "ID obiektu", self.object_id)
        self._entry(card, "ID klucza", self.key_id)
        actions = tk.Frame(card, bg=PANEL); actions.pack(fill="x", padx=14, pady=10)
        ttk.Button(actions, text="Utwórz manifest…", style="Accent.TButton", command=self._create_fingerprint).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Zweryfikuj manifest…", command=self._verify_fingerprint).pack(side="left")
        self.fp_output = tk.Text(card, height=5, bg="#0C1421", fg=ACCENT, insertbackground=FG, relief="flat", wrap="word", font=("Consolas", 9))
        self.fp_output.pack(fill="x", padx=14, pady=(0, 14))
        rep = self._section(self.fp_tab, "Odcisk szyfrogramu", "Policz SHA-256 z domenowym rozdzieleniem dla dowolnego pliku szyfrogramu — także dużego pliku, bez wczytywania go w całości do RAM.")
        ttk.Button(rep, text="Wybierz szyfrogram i oblicz odcisk…", command=self._representation).pack(anchor="w", padx=14, pady=(0, 12))

    def _build_trust(self):
        card = self._section(self.trust_tab, "03  AIRP · zewnętrzne zaufanie", "Ta sekcja łączy odciski z podpisanym dziennikiem AIRP i quorum niezależnych świadków. Każdy endpoint powinien być zarządzany w osobnej domenie administracyjnej.")
        self._entry(card, "Klucz podpisujący", self.signer_file, browse=self._pick_signer)
        self._entry(card, "Stary plik klucza", self.old_key_file, browse=self._pick_old_key)
        self._entry(card, "ID starego klucza", self.old_key_id)
        self._entry(card, "Hasło PEM", self.signer_password, secret=True)
        self._entry(card, "Baza AIRP", self.ledger_path, browse=self._pick_ledger)
        tk.Label(card, text="Świadkowie — jeden wpis na linię: HTTPS_URL | BEARER_TOKEN (tokeny nie są zapisywane)", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(8, 3))
        self.anchors = tk.Text(card, height=5, bg="#0C1421", fg=FG, insertbackground=FG, relief="flat", wrap="none", font=("Consolas", 9))
        self.anchors.pack(fill="x", padx=14, pady=(0, 10))
        row = tk.Frame(card, bg=PANEL); row.pack(fill="x", padx=14, pady=(0, 12))
        ttk.Button(row, text="Zarejestruj klucz", style="Accent.TButton", command=self._register_identity).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="Rotuj klucz", command=self._rotate_identity).pack(side="left", padx=6)
        ttk.Button(row, text="Sprawdź / ponów quorum", command=self._verify_quorum).pack(side="left", padx=6)
        info = self._section(self.trust_tab, "Polityka bezpieczeństwa", "Quorum to ścisła większość skonfigurowanych świadków. Dla odporności administracyjnej skonfiguruj co najmniej 3 niezależne endpointy. Przy braku quorum zdarzenie pozostaje lokalne i jest jawnie oznaczone jako niezakotwiczone — aplikacja nie pokazuje fałszywego sukcesu.")

    def _refresh_mode(self):
        if self.mode.get() == "key":
            self.pass_row.pack_forget()
            self.key_row.pack(fill="x")
        else:
            self.key_row.pack_forget()
            self.pass_row.pack(fill="x")

    def _pick_source(self):
        p = filedialog.askopenfilename()
        if p:
            self.source.set(p)
            self.refresh_dashboard()

    def _pick_key(self):
        p = filedialog.askopenfilename(title="Wybierz 32-bajtowy plik klucza")
        if p: self.key_file.set(p)

    def _pick_old_key(self):
        p = filedialog.askopenfilename(title="Wybierz poprzedni plik klucza")
        if p: self.old_key_file.set(p)

    def _pick_signer(self):
        p = filedialog.askopenfilename(title="Wybierz klucz podpisujący Ed25519 (PEM)")
        if p: self.signer_file.set(p)

    def _pick_ledger(self):
        p = filedialog.asksaveasfilename(title="Lokalna baza AIRP", initialfile="identity.sqlite3")
        if p: self.ledger_path.set(p)

    def _read_key(self):
        if self.mode.get() == "password":
            value = self.password.get()
            if not value: raise HelixProError("Wpisz hasło.")
            return {"password": value}
        path = self.key_file.get()
        if not path: raise HelixProError("Wybierz plik klucza.")
        with open(path, "rb") as f: key = f.read(33)
        if len(key) != 32: raise HelixProError("Klucz musi mieć dokładnie 32 bajty.")
        return {"key": key}

    def _generate_key(self):
        path = filedialog.asksaveasfilename(title="Zapisz nowy klucz", defaultextension=".key", initialfile="helix.key")
        if not path: return
        if os.path.exists(path):
            messagebox.showerror("Plik istnieje", "Wybierz inną nazwę. Istniejący klucz nie został nadpisany."); return
        with open(path, "xb") as f: f.write(generate_key())
        self.key_file.set(path); self.mode.set("key"); self._refresh_mode()
        self.status.set("Wygenerowano klucz. Zrób bezpieczną kopię poza urządzeniem.")

    def _encrypt(self):
        try:
            src = self.source.get()
            if not src or not os.path.isfile(src): raise HelixProError("Wybierz istniejący plik.")
            kwargs = self._read_key()
            out = filedialog.asksaveasfilename(title="Zapisz zaszyfrowany plik", initialfile=os.path.basename(src)+".helixpro", defaultextension=".helixpro")
            if not out: return
            if os.path.abspath(out) == os.path.abspath(src): raise HelixProError("Plik wynikowy nie może być źródłowym.")
            if os.path.exists(out) and not messagebox.askyesno("Nadpisanie", "Plik istnieje. Nadpisać?"): return
            encrypt_file_with_name(src, out, compress=True, **kwargs)
            self.source.set(out)
            self.refresh_dashboard()
            self.status.set("Szyfrowanie zakończone. Oryginalna nazwa jest zapisana wewnątrz szyfrogramu.")
            messagebox.showinfo("Helix-Lock", "Plik został zaszyfrowany.")
        except (OSError, HelixProError) as exc: messagebox.showerror("Szyfrowanie", str(exc))

    def _decrypt(self):
        try:
            src = self.source.get()
            if not src or not os.path.isfile(src): raise HelixProError("Wybierz istniejący plik.")
            fmt = detect_format(src)
            if fmt == "unknown": raise HelixProError("Nie rozpoznano formatu Helix-Lock.")
            if fmt == "counter": raise HelixProError("Format CounterLock wymaga weryfikacji licznika przez AIRPCounterLock i trwały rejestr. Odszyfrowanie bez tej kontroli jest zablokowane.")
            kwargs = self._read_key()
            if fmt == "named":
                name, data = decrypt_bytes_with_name(src, **kwargs)
                out = filedialog.asksaveasfilename(title="Zapisz odszyfrowany plik", initialfile=name)
                if not out: return
                if os.path.exists(out) and not messagebox.askyesno("Nadpisanie", "Plik istnieje. Nadpisać?"): return
                with open(out, "xb" if not os.path.exists(out) else "wb") as f: f.write(data)
            else:
                out = filedialog.asksaveasfilename(title="Zapisz odszyfrowany plik", initialfile=os.path.basename(src).removesuffix(".helixpro"))
                if not out: return
                if os.path.exists(out) and not messagebox.askyesno("Nadpisanie", "Plik istnieje. Nadpisać?"): return
                decrypt_file(src, out, **kwargs)
            self.refresh_dashboard()
            self.status.set("Deszyfrowanie zakończone.")
            messagebox.showinfo("Helix-Lock", "Plik został odszyfrowany.")
        except (OSError, HelixProError) as exc: messagebox.showerror("Deszyfrowanie", str(exc))

    def _create_fingerprint(self):
        try:
            if self.mode.get() == "password": raise HelixProError("Odcisk klucza wymaga pliku klucza 32 B, nie hasła.")
            key = self._read_key()["key"]
            fp = create_key_fingerprint(key, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip())
            raw = json.dumps(fp.to_dict(), indent=2, ensure_ascii=False)
            path = filedialog.asksaveasfilename(title="Zapisz manifest", defaultextension=".json", initialfile="airp-key-fingerprint.json")
            if not path: return
            if os.path.exists(path): raise HelixProError("Manifest już istnieje. Wybierz inną nazwę; nie nadpisuję go.")
            with open(path, "x", encoding="utf-8") as f: f.write(raw + "\n")
            self.fp_output.delete("1.0", "end"); self.fp_output.insert("1.0", raw)
            self.status.set("Manifest odcisku zapisany. Nie zawiera sekretnego klucza.")
        except (OSError, HelixProError) as exc: messagebox.showerror("Odcisk klucza", str(exc))

    def _verify_fingerprint(self):
        try:
            if self.mode.get() == "password": raise HelixProError("Wybierz tryb pliku-klucza.")
            path = filedialog.askopenfilename(title="Wczytaj manifest", filetypes=[("JSON", "*.json")])
            if not path: return
            with open(path, encoding="utf-8") as f: fp = KeyFingerprint.from_dict(json.load(f))
            key = self._read_key()["key"]
            ok = verify_key_fingerprint(key, fp, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip())
            if ok:
                self.status.set("Odcisk zgodny.")
                messagebox.showinfo("Weryfikacja", "Klucz i kontekst pasują do manifestu. To nie jest dowód uprawnień.")
            else:
                self.status.set("Niezgodność odcisku.")
                messagebox.showwarning("Weryfikacja", "Klucz lub identyfikator obiektu/klucza nie pasuje.")
        except (OSError, ValueError, HelixProError) as exc: messagebox.showerror("Weryfikacja", str(exc))

    def _representation(self):
        path = filedialog.askopenfilename(title="Wybierz szyfrogram")
        if not path: return
        try:
            value = representation_fingerprint_file(path)
            self.clipboard_clear(); self.clipboard_append(value)
            self.status.set("Odcisk reprezentacji skopiowano do schowka: " + value)
            messagebox.showinfo("Odcisk szyfrogramu", value + "\n\nSkopiowano do schowka.")
        except HelixProError as exc: messagebox.showerror("Odcisk szyfrogramu", str(exc))

    def _identity_manager(self):
        signer_path = self.signer_file.get().strip()
        if not signer_path or not os.path.isfile(signer_path): raise HelixProError("Wybierz prywatny klucz podpisujący Ed25519 w formacie PEM.")
        password = self.signer_password.get().encode("utf-8") if self.signer_password.get() else None
        with open(signer_path, "rb") as f: signer = serialization.load_pem_private_key(f.read(), password=password)
        if not isinstance(signer, Ed25519PrivateKey): raise HelixProError("Klucz podpisujący musi być Ed25519.")
        lines = [x.strip() for x in self.anchors.get("1.0", "end").splitlines() if x.strip()]
        if len(lines) < 3: raise HelixProError("Skonfiguruj co najmniej 3 niezależne endpointy quorum.")
        anchors = []
        for line in lines:
            parts = [x.strip() for x in line.split("|", 1)]
            if len(parts) != 2: raise HelixProError("Każdy świadek musi mieć format HTTPS_URL | BEARER_TOKEN.")
            anchors.append(HTTPTrustAnchor(parts[0], parts[1]))
        quorum = QuorumTrustAnchor(anchors)
        ledger = AIRPIntegrityLedger(self.ledger_path.get(), signer, trust_anchor=quorum)
        return AIRPIdentityManager(ledger)

    def _register_identity(self):
        try:
            if self.mode.get() == "password": raise HelixProError("Rejestracja fingerprint wymaga pliku klucza.")
            key = self._read_key()["key"]
            manager = self._identity_manager()
            result = manager.register_key(key, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip())
            if result.anchored:
                self.status.set("AIRP: odcisk zakotwiczony w quorum.")
                messagebox.showinfo("AIRP / Quorum", result.message)
            else:
                self.status.set("AIRP: lokalny wpis oczekuje na quorum.")
                messagebox.showwarning("AIRP / Quorum — pending", result.message + "\n\nStatus: " + result.anchor_status)
        except (OSError, ValueError, TypeError, HelixProError) as exc: messagebox.showerror("AIRP / Quorum", str(exc))

    def _rotate_identity(self):
        try:
            old_path = self.old_key_file.get().strip()
            if not old_path or not os.path.isfile(old_path):
                raise HelixProError("Wskaż poprzedni plik klucza.")
            with open(old_path, "rb") as f: old_key = f.read(33)
            new_key = self._read_key()["key"]
            if len(old_key) != 32: raise HelixProError("Poprzedni klucz musi mieć dokładnie 32 bajty.")
            manager = self._identity_manager()
            signer_path = self.signer_file.get().strip()
            password = self.signer_password.get().encode("utf-8") if self.signer_password.get() else None
            with open(signer_path, "rb") as f: signer = serialization.load_pem_private_key(f.read(), password=password)
            result = manager.rotate_key(
                old_key, new_key, object_id=self.object_id.get().strip(),
                old_key_id=self.old_key_id.get().strip(), new_key_id=self.key_id.get().strip(),
                signer=signer,
            )
            if result.anchored:
                self.status.set("AIRP: rotacja klucza potwierdzona przez quorum.")
                messagebox.showinfo("AIRP / rotacja", result.message)
            else:
                self.status.set("AIRP: rotacja lokalna — oczekuje na quorum.")
                messagebox.showwarning("AIRP / rotacja — pending", result.message + "\n\nStatus: " + result.anchor_status)
        except (OSError, ValueError, TypeError, HelixProError) as exc:
            messagebox.showerror("AIRP / rotacja", str(exc))

    def _verify_quorum(self):
        try:
            manager = self._identity_manager()
            result = manager.retry_anchor()
            self.status.set("AIRP status: " + result.status)
            messagebox.showinfo("AIRP / Quorum", f"Status: {result.status}\nLokalna sekwencja: {result.local_sequence}\nZakotwiczona sekwencja: {result.anchored_sequence}")
        except (OSError, ValueError, HelixProError) as exc: messagebox.showerror("AIRP / Quorum", str(exc))


def main():
    app = HelixLockApp()
    app.mainloop()


if __name__ == "__main__":
    main()
