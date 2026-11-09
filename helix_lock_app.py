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
    HelixProError, atomic_write_bytes, decrypt_bytes_with_name, decrypt_file, detect_format,
    encrypt_file_with_name, generate_key, write_new_key_file,
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEDGER = os.path.join(os.path.expanduser("~"), ".helix_lock", "identity.sqlite3")
BG, PANEL, ACCENT, FG, MUTED = "#101827", "#182437", "#54D6A0", "#F2F6FC", "#9FB0C5"

def paths_refer_to_same_file(source: str, destination: str) -> bool:
    """Reject same-path, symlink, and hard-link aliases for source/output."""
    source_abs = os.path.abspath(source)
    destination_abs = os.path.abspath(destination)
    if os.path.normcase(os.path.realpath(source_abs)) == os.path.normcase(os.path.realpath(destination_abs)):
        return True
    try:
        return os.path.exists(destination_abs) and os.path.samefile(source_abs, destination_abs)
    except OSError:
        return False



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

    def _tr(self, polish, english):
        # Windows users asked for bilingual labels; Linux/macOS keep concise English UI.
        return english + " / " + polish if os.name == "nt" else english

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
        tk.Label(head, text=self._tr("Szyfrowanie plików  ·  Tożsamość kluczy  ·  Zaufanie AIRP", "File encryption · Key identity · AIRP trust"), bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=(80, 0))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        # Primary workflow comes first: file -> key -> operation.
        self.file_tab = ttk.Frame(self.tabs); self.tabs.add(self.file_tab, text=self._tr("Plik i klucz", "File & key"))
        self.settings_tab = ttk.Frame(self.tabs); self.tabs.add(self.settings_tab, text=self._tr("Ustawienia", "Settings"))
        self.info_tab = ttk.Frame(self.tabs); self.tabs.add(self.info_tab, text=self._tr("Informacje", "Information"))
        self.dashboard_tab = ttk.Frame(self.tabs); self.tabs.add(self.dashboard_tab, text=self._tr("Przegląd bezpieczeństwa", "Security overview"))
        self.fp_tab = ttk.Frame(self.tabs); self.tabs.add(self.fp_tab, text=self._tr("Odcisk klucza", "Key fingerprint"))
        self.trust_tab = ttk.Frame(self.tabs); self.tabs.add(self.trust_tab, text=self._tr("AIRP / Quorum", "AIRP / Quorum"))
        self._build_files()
        self._build_settings()
        self._build_information()
        self._build_dashboard()
        self._build_fingerprint()
        self._build_trust()
        self.tabs.select(self.file_tab)
        self.status = tk.StringVar(value=self._tr("Gotowy. Klucze pozostają lokalnie na Twoim urządzeniu.", "Ready. Keys stay on this device."))
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
            ttk.Button(row, text=self._tr("Wybierz…", "Browse…"), command=browse).pack(side="left")
        return entry


    def _metric(self, parent, title, value, note):
        card = tk.Frame(parent, bg=PANEL, highlightbackground="#2A3B53", highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(card, textvariable=value, bg=PANEL, fg=ACCENT, font=("Segoe UI", 19, "bold")).pack(anchor="w", padx=12)
        tk.Label(card, text=note, bg=PANEL, fg=MUTED, font=("Segoe UI", 8), wraplength=210, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

    def _build_dashboard(self):
        intro = self._section(self.dashboard_tab, self._tr("CENTRUM BEZPIECZENSTWA", "SECURITY OVERVIEW"), self._tr("Podglad lokalnego rejestru AIRP i wybranego pliku. Brak danych nie oznacza pozytywnego wyniku kontroli.", "Local AIRP ledger and selected-file status. Missing data never means a passed security check."))
        ttk.Button(intro, text=self._tr("Odswiez podglad", "Refresh overview"), command=self.refresh_dashboard).pack(anchor="e", padx=14, pady=(0, 10))
        row1 = tk.Frame(self.dashboard_tab, bg=BG); row1.pack(fill="x", padx=10)
        row2 = tk.Frame(self.dashboard_tab, bg=BG); row2.pack(fill="x", padx=10)
        self.dash_chain = tk.StringVar(value="—")
        self.dash_sequence = tk.StringVar(value="—")
        self.dash_anchor = tk.StringVar(value="NIEZNANY")
        self.dash_counter = tk.StringVar(value="—")
        self.dash_file = tk.StringVar(value=self._tr("Nie wybrano", "No file selected"))
        self.dash_events = tk.StringVar(value="—")
        self._metric(row1, self._tr("LANCUCH AIRP", "AIRP CHAIN"), self.dash_chain, self._tr("Dane lokalne; nie oznaczaja potwierdzenia quorum.", "Local data; quorum is not confirmed."))
        self._metric(row1, self._tr("SEKWENCJA", "SEQUENCE"), self.dash_sequence, self._tr("Liczba zdarzen w lokalnym dzienniku.", "Events in the local ledger."))
        self._metric(row1, self._tr("CHECKPOINT", "CHECKPOINT"), self.dash_anchor, self._tr("Stan zewnetrznego anchor wymaga osobnej weryfikacji.", "External trust anchor must be checked separately."))
        self._metric(row2, self._tr("LICZNIK COUNTERLOCK", "COUNTERLOCK COUNTER"), self.dash_counter, self._tr("Ostatni licznik zapisany w lokalnym dzienniku AIRP.", "Latest counter recorded in the AIRP ledger."))
        self._metric(row2, self._tr("FORMAT PLIKU", "FILE FORMAT"), self.dash_file, self._tr("Rozpoznanie naglowka, nie weryfikacja kluczem.", "Header detection only; not key verification."))
        self._metric(row2, self._tr("ZDARZENIA", "EVENTS"), self.dash_events, self._tr("Liczba wpisow w dzienniku AIRP.", "Number of AIRP ledger entries."))
        history = self._section(self.dashboard_tab, self._tr("OS CZASU ZDARZEN", "EVENT TIMELINE"), self._tr("Ostatnie wpisy AIRP; bez kluczy, hasel i tresci plikow.", "Recent AIRP events; no keys, passwords, or file contents."))
        self.dash_history = tk.Text(history, height=9, bg="#0C1421", fg=FG, insertbackground=FG, relief="flat", wrap="word", font=("Consolas", 9), state="disabled")
        self.dash_history.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        tk.Label(self.dashboard_tab, text=self._tr("WAZNE: lokalna baza SQLite sama nie chroni przed cofaniem calej bazy. Ochrona przed rollbackiem wymaga niezaleznego Trust Anchor / quorum.", "IMPORTANT: a local SQLite database cannot prevent rollback of the database itself. Rollback protection requires an independent trust anchor / quorum."), bg=BG, fg="#F2C879", font=("Segoe UI", 9), wraplength=730, justify="left").pack(fill="x", padx=18, pady=(4, 8))

    def refresh_dashboard(self):
        self.dash_file.set(self._tr("Nie wybrano", "No file selected"))
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
                    self.dash_file.set(self._tr("Nieznany / zwykly", "Unknown / plain file"))
            except OSError:
                self.dash_file.set(self._tr("Nie mozna odczytac", "Cannot read file"))
        else:
            self.dash_counter.set("—")

        db_path = self.ledger_path.get().strip() if hasattr(self, "ledger_path") else DEFAULT_LEDGER
        self.dash_chain.set(self._tr("BRAK BAZY", "NO DATABASE"))
        self.dash_sequence.set("—")
        self.dash_anchor.set(self._tr("NIE SPRAWDZONO", "NOT CHECKED"))
        self.dash_events.set("—")
        history_lines = [self._tr("Brak lokalnej bazy AIRP. Zarejestruj klucz w zakladce AIRP / Quorum.", "No local AIRP database. Register a key in AIRP / Quorum.")]
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
                        self.dash_chain.set(("PUSTY" if total == 0 else "CHAIN OK") if chain_valid else "CHAIN BLEDNY")
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
                            self.dash_counter.set(self._tr("BRAK WPISOW", "NO ENTRIES"))
                        if not history_lines:
                            history_lines = [self._tr("Dziennik jest pusty.", "Ledger is empty.")]
                        history_lines.extend(["", "Uwaga: lokalny odczyt nie potwierdza stanu zewnetrznego quorum."])
                    else:
                        history_lines = [self._tr("Wybrana baza nie zawiera tabeli dziennika AIRP.", "Selected database has no AIRP ledger table.")]
            except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
                self.dash_chain.set(self._tr("BLAD ODCZYTU", "READ ERROR"))
                history_lines = [self._tr("Nie udalo sie odczytac bazy AIRP: ", "Could not read AIRP database: ") + str(exc)]
        self.dash_history.configure(state="normal")
        self.dash_history.delete("1.0", "end")
        self.dash_history.insert("1.0", "\\n".join(history_lines))
        self.dash_history.configure(state="disabled")

    def _build_files(self):
        card = self._section(self.file_tab, self._tr("01  Szyfruj / odszyfruj", "01  Encrypt / decrypt"), self._tr("Wybierz plik, sposób uwierzytelnienia i jedną operację. Program sam podpowie nazwę pliku wynikowego.", "Choose a file and an authentication method, then encrypt or decrypt."))
        self._entry(card, self._tr("Plik źródłowy", "Source file"), self.source, browse=self._pick_source)
        row = tk.Frame(card, bg=PANEL); row.pack(fill="x", padx=14, pady=7)
        ttk.Radiobutton(row, text=self._tr("Plik-klucz (zalecane)", "Key file (recommended)"), variable=self.mode, value="key", command=self._refresh_mode).pack(side="left")
        ttk.Radiobutton(row, text=self._tr("Hasło", "Password"), variable=self.mode, value="password", command=self._refresh_mode).pack(side="left", padx=18)
        self.key_row = tk.Frame(card, bg=PANEL); self.key_row.pack(fill="x")
        self._entry(self.key_row, "Plik klucza", self.key_file, browse=self._pick_key)
        ttk.Button(card, text=self._tr("Wygeneruj nowy klucz…", "Generate key…"), command=self._generate_key).pack(anchor="e", padx=14, pady=5)
        self.pass_row = tk.Frame(card, bg=PANEL)
        self._entry(self.pass_row, self._tr("Hasło", "Password"), self.password, secret=True)
        actions = tk.Frame(card, bg=PANEL); actions.pack(fill="x", padx=14, pady=(12, 14))
        ttk.Button(actions, text=self._tr("🔒  Szyfruj", "🔒  Encrypt"), style="Accent.TButton", command=self._encrypt).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(actions, text=self._tr("🔓  Odszyfruj", "🔓  Decrypt"), command=self._decrypt).pack(side="left", expand=True, fill="x", padx=(6, 0))
        ttk.Button(actions, text=self._tr("API · Lista plików", "API · File queue"), command=self._open_api_window).pack(side="left", padx=(12, 0))
        self._refresh_mode()
        note = self._section(self.file_tab, self._tr("Ważne", "Important"), self._tr("Zachowaj kopię klucza poza komputerem z zaszyfrowanymi danymi. Bez klucza lub hasła odzyskanie treści nie będzie możliwe. Odcisk klucza nie zastępuje klucza.", "Keep a backup of the key away from the encrypted data. Without the key or password, the data cannot be recovered. A fingerprint is not a key."))

    def _open_api_window(self):
        """Open a compact, non-modal batch/API workspace (at most 1/4 screen area)."""
        if getattr(self, "api_window", None) is not None and self.api_window.winfo_exists():
            self.api_window.deiconify()
            self.api_window.lift()
            return

        win = tk.Toplevel(self)
        self.api_window = win
        win.title("Helix-Lock · API / kolejka plików")
        screen_w, screen_h = win.winfo_screenwidth(), win.winfo_screenheight()
        width, height = max(1, screen_w // 2), max(1, screen_h // 2)
        width, height = min(width, screen_w), min(height, screen_h)
        x, y = max(0, (screen_w - width) // 2), max(0, (screen_h - height) // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
        win.maxsize(width, height)
        win.resizable(True, True)
        win.configure(bg=BG)
        win.transient(self)

        self.api_files = []
        self.api_output_dir = tk.StringVar(value=os.path.expanduser("~"))
        self.api_operation = tk.StringVar(value="encrypt")
        self.api_progress = tk.StringVar(value=self._tr("Dodaj pliki do kolejki.", "Add files to the queue."))
        head = tk.Frame(win, bg=BG)
        head.pack(fill="x", padx=12, pady=(10, 5))
        tk.Label(head, text="HELIX API · BATCH", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(head, text=self._tr("Kolejka plików · przetwarzanie sekwencyjne",
                                     "File queue · sequential processing"),
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")

        toolbar = tk.Frame(win, bg=BG); toolbar.pack(fill="x", padx=10, pady=4)
        ttk.Button(toolbar, text=self._tr("Dodaj pliki…", "Add files…"),
                   command=self._api_add_files).pack(side="left", padx=2)
        ttk.Button(toolbar, text=self._tr("Usuń zaznaczone", "Remove selected"),
                   command=self._api_remove_selected).pack(side="left", padx=2)
        ttk.Button(toolbar, text=self._tr("Wyczyść", "Clear"),
                   command=self._api_clear_files).pack(side="left", padx=2)

        list_frame = tk.Frame(win, bg=PANEL); list_frame.pack(fill="both", expand=True, padx=10, pady=4)
        columns = ("file", "status")
        self.api_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=6)
        self.api_tree.heading("file", text=self._tr("Plik", "File"))
        self.api_tree.heading("status", text=self._tr("Stan", "Status"))
        self.api_tree.column("file", width=max(160, width - 150), stretch=True)
        self.api_tree.column("status", width=100, stretch=False)
        self.api_tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.api_tree.yview)
        scroll.pack(side="right", fill="y")
        self.api_tree.configure(yscrollcommand=scroll.set)

        out = tk.Frame(win, bg=BG); out.pack(fill="x", padx=10, pady=3)
        tk.Label(out, text=self._tr("Katalog wynikowy", "Output folder"), bg=BG, fg=MUTED).pack(side="left")
        ttk.Entry(out, textvariable=self.api_output_dir).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(out, text=self._tr("Wybierz…", "Browse…"), command=self._api_pick_output).pack(side="right")

        opts = tk.Frame(win, bg=BG); opts.pack(fill="x", padx=10, pady=2)
        ttk.Radiobutton(opts, text=self._tr("Szyfruj", "Encrypt"), variable=self.api_operation,
                        value="encrypt").pack(side="left")
        ttk.Radiobutton(opts, text=self._tr("Odszyfruj", "Decrypt"), variable=self.api_operation,
                        value="decrypt").pack(side="left", padx=10)
        ttk.Button(opts, text=self._tr("Wykonaj kolejkę", "Run queue"),
                   style="Accent.TButton", command=self._api_process).pack(side="right")
        tk.Label(win, textvariable=self.api_progress, bg=BG, fg=MUTED,
                 anchor="w", wraplength=max(250, width - 30)).pack(fill="x", padx=12, pady=(2, 8))
        win.protocol("WM_DELETE_WINDOW", win.withdraw)

    def _api_add_files(self):
        paths = filedialog.askopenfilenames(title=self._tr("Dodaj pliki do kolejki", "Add files to queue"))
        known = {os.path.normcase(os.path.abspath(p)) for p in self.api_files}
        added = 0
        for path in paths:
            normalized = os.path.normcase(os.path.abspath(path))
            if os.path.isfile(path) and normalized not in known:
                self.api_files.append(path)
                self.api_tree.insert("", "end", iid=str(len(self.api_files) - 1),
                                     values=(os.path.basename(path), self._tr("Oczekuje", "Queued")))
                known.add(normalized)
                added += 1
        self.api_progress.set(self._tr(f"Dodano: {added} · Łącznie: {len(self.api_files)}",
                                       f"Added: {added} · Total: {len(self.api_files)}"))

    def _api_remove_selected(self):
        selected = set(self.api_tree.selection())
        if not selected:
            return
        self.api_files = [p for i, p in enumerate(self.api_files) if str(i) not in selected]
        for item in self.api_tree.get_children():
            self.api_tree.delete(item)
        for i, path in enumerate(self.api_files):
            self.api_tree.insert("", "end", iid=str(i),
                                 values=(os.path.basename(path), self._tr("Oczekuje", "Queued")))
        self.api_progress.set(self._tr(f"Pliki w kolejce: {len(self.api_files)}",
                                       f"Files in queue: {len(self.api_files)}"))

    def _api_clear_files(self):
        self.api_files.clear()
        for item in self.api_tree.get_children():
            self.api_tree.delete(item)
        self.api_progress.set(self._tr("Kolejka wyczyszczona.", "Queue cleared."))

    def _api_pick_output(self):
        path = filedialog.askdirectory(title=self._tr("Wybierz katalog wynikowy", "Choose output folder"))
        if path:
            self.api_output_dir.set(path)

    def _api_process(self):
        if not self.api_files:
            self.api_progress.set(self._tr("Kolejka jest pusta.", "Queue is empty."))
            return
        out_dir = self.api_output_dir.get().strip()
        if not out_dir or not os.path.isdir(out_dir):
            messagebox.showerror("Helix-Lock API", self._tr("Wybierz istniejący katalog wynikowy.",
                                                            "Choose an existing output folder."))
            return
        try:
            kwargs = self._read_key()
        except (OSError, HelixProError) as exc:
            messagebox.showerror("Helix-Lock API", str(exc))
            return

        total, completed, failed, skipped = len(self.api_files), 0, 0, 0
        for index, src in enumerate(list(self.api_files)):
            item_id = str(index)
            try:
                if not os.path.isfile(src):
                    raise HelixProError(self._tr("Plik źródłowy nie istnieje.", "Source file does not exist."))
                if self.api_operation.get() == "encrypt":
                    out = os.path.join(out_dir, os.path.basename(src) + ".helixpro")
                    if os.path.exists(out):
                        skipped += 1
                        self.api_tree.set(item_id, "status", self._tr("Pominięto", "Skipped"))
                        continue
                    encrypt_file_with_name(src, out, compress=True, **kwargs)
                else:
                    fmt = detect_format(src)
                    if fmt == "counter":
                        skipped += 1
                        self.api_tree.set(item_id, "status", "CounterLock")
                        continue
                    if fmt == "named":
                        original_name, payload = decrypt_bytes_with_name(src, **kwargs)
                        out = os.path.join(out_dir, original_name)
                        if os.path.exists(out):
                            skipped += 1
                            self.api_tree.set(item_id, "status", self._tr("Pominięto", "Skipped"))
                            continue
                        atomic_write_bytes(out, payload)
                    elif fmt == "plain":
                        name = os.path.basename(src)
                        if name.lower().endswith(".helixpro"):
                            name = name[:-len(".helixpro")]
                        out = os.path.join(out_dir, name or "decrypted.bin")
                        if os.path.exists(out):
                            skipped += 1
                            self.api_tree.set(item_id, "status", self._tr("Pominięto", "Skipped"))
                            continue
                        decrypt_file(src, out, **kwargs)
                    else:
                        skipped += 1
                        self.api_tree.set(item_id, "status", self._tr("Nieznany format", "Unknown format"))
                        continue
                completed += 1
                self.api_tree.set(item_id, "status", self._tr("Gotowe", "Done"))
            except (OSError, HelixProError, ValueError) as exc:
                failed += 1
                self.api_tree.set(item_id, "status", self._tr("Błąd", "Error"))
                self.api_progress.set(self._tr(f"{index + 1}/{total} · Błąd: {os.path.basename(src)} — {exc}",
                                               f"{index + 1}/{total} · Error: {os.path.basename(src)} — {exc}"))
            self.api_window.update_idletasks()
            self.api_progress.set(self._tr(f"Postęp {index + 1}/{total} · OK {completed} · Błędy {failed} · Pominięte {skipped}",
                                           f"Progress {index + 1}/{total} · OK {completed} · Errors {failed} · Skipped {skipped}"))
            self.api_window.update()
        self.status.set(self._tr(f"API: zakończono kolejkę · OK {completed} · błędy {failed} · pominięte {skipped}",
                                 f"API: queue finished · OK {completed} · errors {failed} · skipped {skipped}"))
        self.refresh_dashboard()

    def _build_settings(self):
        card = self._section(
            self.settings_tab,
            self._tr("USTAWIENIA", "SETTINGS"),
            self._tr("Wybierz sposób pracy z kluczem. Ustawienie jest współdzielone z ekranem plików.",
                     "Choose how to use your key. This setting is shared with the file screen."),
        )
        ttk.Radiobutton(
            card, text=self._tr("Plik klucza", "Key file"), variable=self.mode,
            value="key", command=self._refresh_mode,
        ).pack(anchor="w", padx=14, pady=5)
        ttk.Radiobutton(
            card, text=self._tr("Hasło", "Password"), variable=self.mode,
            value="password", command=self._refresh_mode,
        ).pack(anchor="w", padx=14, pady=(0, 12))
        ttk.Button(
            card, text=self._tr("Wróć do pliku i klucza", "Back to file & key"),
            command=lambda: self.tabs.select(self.file_tab),
        ).pack(anchor="w", padx=14, pady=(0, 12))

    def _build_information(self):
        card = self._section(
            self.info_tab,
            self._tr("INFORMACJE", "INFORMATION"),
            self._tr("Najpierw wybierz plik i klucz na pierwszej karcie. Moduły AIRP są opcjonalne.",
                     "Start with a file and key on the first tab. AIRP modules are optional."),
        )
        tk.Label(
            card, text=self._tr(
                "Klucz przechowuj oddzielnie od zaszyfrowanych danych. "
                "Utrata klucza może uniemożliwić odzyskanie pliku.",
                "Store your key separately from encrypted data. "
                "Losing the key can make file recovery impossible."),
            bg=PANEL, fg=FG, wraplength=680, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 12))
        ttk.Button(
            card, text=self._tr("Przejdź do pracy z plikiem", "Go to file workflow"),
            command=lambda: self.tabs.select(self.file_tab),
        ).pack(anchor="w", padx=14, pady=(0, 12))

    def _build_fingerprint(self):
        card = self._section(self.fp_tab, self._tr("02  Tożsamość klucza", "02  Key identity"), self._tr("Utwórz odcisk powiązany z identyfikatorem obiektu i klucza. Manifest nie zawiera klucza ani hasła.", "Create a fingerprint bound to object and key IDs. The manifest contains no key or password."))
        self._entry(card, "Plik klucza", self.key_file, browse=self._pick_key)
        self._entry(card, self._tr("ID obiektu", "Object ID"), self.object_id)
        self._entry(card, self._tr("ID klucza", "Key ID"), self.key_id)
        actions = tk.Frame(card, bg=PANEL); actions.pack(fill="x", padx=14, pady=10)
        ttk.Button(actions, text=self._tr("Utwórz manifest…", "Create manifest…"), style="Accent.TButton", command=self._create_fingerprint).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text=self._tr("Zweryfikuj manifest…", "Verify manifest…"), command=self._verify_fingerprint).pack(side="left")
        self.fp_output = tk.Text(card, height=5, bg="#0C1421", fg=ACCENT, insertbackground=FG, relief="flat", wrap="word", font=("Consolas", 9))
        self.fp_output.pack(fill="x", padx=14, pady=(0, 14))
        rep = self._section(self.fp_tab, self._tr("Odcisk szyfrogramu", "Ciphertext fingerprint"), self._tr("Policz SHA-256 z domenowym rozdzieleniem dla dowolnego pliku szyfrogramu — także dużego pliku, bez wczytywania go w całości do RAM.", "Calculate a domain-separated SHA-256 fingerprint, including for large files, without loading the whole file into memory."))
        ttk.Button(rep, text=self._tr("Wybierz szyfrogram i oblicz odcisk…", "Select ciphertext and calculate fingerprint…"), command=self._representation).pack(anchor="w", padx=14, pady=(0, 12))

    def _build_trust(self):
        card = self._section(self.trust_tab, self._tr("03  AIRP · zewnętrzne zaufanie", "03  AIRP · External trust"), self._tr("Ta sekcja łączy odciski z podpisanym dziennikiem AIRP i quorum niezależnych świadków. Każdy endpoint powinien być zarządzany w osobnej domenie administracyjnej.", "Connect fingerprints to the signed AIRP ledger and independent witness quorum. Each endpoint should have separate administration."))
        self._entry(card, self._tr("Klucz podpisujący", "Signing key"), self.signer_file, browse=self._pick_signer)
        self._entry(card, self._tr("Stary plik klucza", "Previous key file"), self.old_key_file, browse=self._pick_old_key)
        self._entry(card, self._tr("ID starego klucza", "Previous key ID"), self.old_key_id)
        self._entry(card, self._tr("Hasło PEM", "PEM password"), self.signer_password, secret=True)
        self._entry(card, self._tr("Baza AIRP", "AIRP database"), self.ledger_path, browse=self._pick_ledger)
        tk.Label(card, text=self._tr("Świadkowie — jeden wpis na linię: HTTPS_URL | BEARER_TOKEN (tokeny nie są zapisywane)", "Witnesses — one per line: HTTPS_URL | BEARER_TOKEN (tokens are not saved)"), bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(8, 3))
        self.anchors = tk.Text(card, height=5, bg="#0C1421", fg=FG, insertbackground=FG, relief="flat", wrap="none", font=("Consolas", 9))
        self.anchors.pack(fill="x", padx=14, pady=(0, 10))
        row = tk.Frame(card, bg=PANEL); row.pack(fill="x", padx=14, pady=(0, 12))
        ttk.Button(row, text=self._tr("Zarejestruj klucz", "Register key"), style="Accent.TButton", command=self._register_identity).pack(side="left", padx=(0, 6))
        ttk.Button(row, text=self._tr("Rotuj klucz", "Rotate key"), command=self._rotate_identity).pack(side="left", padx=6)
        ttk.Button(row, text=self._tr("Sprawdź / ponów quorum", "Check / retry quorum"), command=self._verify_quorum).pack(side="left", padx=6)
        info = self._section(self.trust_tab, self._tr("Polityka bezpieczeństwa", "Security policy"), self._tr("Quorum to ścisła większość skonfigurowanych świadków. Dla odporności administracyjnej skonfiguruj co najmniej 3 niezależne endpointy. Przy braku quorum zdarzenie pozostaje lokalne i jest jawnie oznaczone jako niezakotwiczone — aplikacja nie pokazuje fałszywego sukcesu.", "Quorum requires a strict majority of configured witnesses. Use at least 3 independently administered endpoints. Without quorum, events remain local and are marked unanchored."))

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
        p = filedialog.askopenfilename(title=self._tr("Wybierz 32-bajtowy plik klucza", "Select a 32-byte key file"))
        if p: self.key_file.set(p)

    def _pick_old_key(self):
        p = filedialog.askopenfilename(title=self._tr("Wybierz poprzedni plik klucza", "Select previous key file"))
        if p: self.old_key_file.set(p)

    def _pick_signer(self):
        p = filedialog.askopenfilename(title=self._tr("Wybierz klucz podpisujący Ed25519 (PEM)", "Select Ed25519 signing key (PEM)"))
        if p: self.signer_file.set(p)

    def _pick_ledger(self):
        p = filedialog.asksaveasfilename(title=self._tr("Lokalna baza AIRP", "Local AIRP database"), initialfile="identity.sqlite3")
        if p: self.ledger_path.set(p)

    def _read_key(self):
        if self.mode.get() == "password":
            value = self.password.get()
            if not value: raise HelixProError(self._tr("Wpisz hasło.", "Enter a password."))
            return {"password": value}
        path = self.key_file.get()
        if not path: raise HelixProError(self._tr("Wybierz plik klucza.", "Select a key file."))
        with open(path, "rb") as f: key = f.read(33)
        if len(key) != 32: raise HelixProError(self._tr("Klucz musi mieć dokładnie 32 bajty.", "Key must be exactly 32 bytes."))
        return {"key": key}

    def _generate_key(self):
        path = filedialog.asksaveasfilename(title=self._tr("Zapisz nowy klucz", "Save new key"), defaultextension=".key", initialfile="helix.key")
        if not path: return
        if os.path.exists(path):
            messagebox.showerror("Plik istnieje", self._tr("Wybierz inną nazwę. Istniejący klucz nie został nadpisany.", "Choose another name. Existing key was not overwritten.")); return
        try:
            write_new_key_file(path, generate_key())
        except OSError as exc:
            messagebox.showerror(self._tr("Nie udało się utworzyć klucza", "Could not create key"), str(exc)); return
        self.key_file.set(path); self.mode.set("key"); self._refresh_mode()
        self.status.set(self._tr("Wygenerowano klucz. Zrób bezpieczną kopię poza urządzeniem.", "Key generated. Store a secure backup away from this device."))

    def _encrypt(self):
        try:
            src = self.source.get()
            if not src or not os.path.isfile(src): raise HelixProError(self._tr("Wybierz istniejący plik.", "Select an existing file."))
            kwargs = self._read_key()
            out = filedialog.asksaveasfilename(title=self._tr("Zapisz zaszyfrowany plik", "Save encrypted file"), initialfile=os.path.basename(src)+".helixpro", defaultextension=".helixpro")
            if not out: return
            if paths_refer_to_same_file(src, out): raise HelixProError(self._tr("Plik wynikowy nie może wskazywać na plik źródłowy.", "Output must not refer to the source file."))
            if os.path.exists(out) and not messagebox.askyesno(self._tr("Nadpisanie", "Overwrite"), self._tr("Plik istnieje. Nadpisać?", "File exists. Overwrite?")): return
            encrypt_file_with_name(src, out, compress=True, **kwargs)
            self.source.set(out)
            self.refresh_dashboard()
            self.status.set(self._tr("Szyfrowanie zakończone. Oryginalna nazwa jest zapisana wewnątrz szyfrogramu.", "Encryption complete. Original filename is stored inside the ciphertext."))
            messagebox.showinfo("Helix-Lock", self._tr("Plik został zaszyfrowany.", "File encrypted."))
        except (OSError, HelixProError) as exc: messagebox.showerror(self._tr("Szyfrowanie", "Encryption"), str(exc))

    def _decrypt(self):
        try:
            src = self.source.get()
            if not src or not os.path.isfile(src): raise HelixProError(self._tr("Wybierz istniejący plik.", "Select an existing file."))
            fmt = detect_format(src)
            if fmt == "unknown": raise HelixProError(self._tr("Nie rozpoznano formatu Helix-Lock.", "Unrecognized Helix-Lock format."))
            if fmt == "counter": raise HelixProError(self._tr("Format CounterLock wymaga weryfikacji licznika przez AIRPCounterLock i trwały rejestr. Odszyfrowanie bez tej kontroli jest zablokowane.", "CounterLock requires AIRPCounterLock and a durable ledger check. Decryption is blocked without that check."))
            kwargs = self._read_key()
            if fmt == "named":
                name, data = decrypt_bytes_with_name(src, **kwargs)
                out = filedialog.asksaveasfilename(title=self._tr("Zapisz odszyfrowany plik", "Save decrypted file"), initialfile=name)
                if not out: return
                if paths_refer_to_same_file(src, out): raise HelixProError(self._tr("Plik wynikowy nie może wskazywać na plik źródłowy.", "Output must not refer to the source file."))
                if os.path.exists(out) and not messagebox.askyesno(self._tr("Nadpisanie", "Overwrite"), self._tr("Plik istnieje. Nadpisać?", "File exists. Overwrite?")): return
                atomic_write_bytes(out, data)
            else:
                out = filedialog.asksaveasfilename(title=self._tr("Zapisz odszyfrowany plik", "Save decrypted file"), initialfile=os.path.basename(src).removesuffix(".helixpro"))
                if not out: return
                if paths_refer_to_same_file(src, out): raise HelixProError(self._tr("Plik wynikowy nie może wskazywać na plik źródłowy.", "Output must not refer to the source file."))
                if os.path.exists(out) and not messagebox.askyesno(self._tr("Nadpisanie", "Overwrite"), self._tr("Plik istnieje. Nadpisać?", "File exists. Overwrite?")): return
                decrypt_file(src, out, **kwargs)
            self.refresh_dashboard()
            self.status.set(self._tr("Deszyfrowanie zakończone.", "Decryption complete."))
            messagebox.showinfo("Helix-Lock", self._tr("Plik został odszyfrowany.", "File decrypted."))
        except (OSError, HelixProError) as exc: messagebox.showerror(self._tr("Deszyfrowanie", "Decryption"), str(exc))

    def _create_fingerprint(self):
        try:
            if self.mode.get() == "password": raise HelixProError(self._tr("Odcisk klucza wymaga pliku klucza 32 B, nie hasła.", "Key fingerprint requires a 32-byte key file, not a password."))
            key = self._read_key()["key"]
            fp = create_key_fingerprint(key, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip())
            raw = json.dumps(fp.to_dict(), indent=2, ensure_ascii=False)
            path = filedialog.asksaveasfilename(title=self._tr("Zapisz manifest", "Save manifest"), defaultextension=".json", initialfile="airp-key-fingerprint.json")
            if not path: return
            if os.path.exists(path): raise HelixProError(self._tr("Manifest już istnieje. Wybierz inną nazwę; nie nadpisuję go.", "Manifest already exists. Choose another name; it will not be overwritten."))
            with open(path, "x", encoding="utf-8") as f: f.write(raw + "\n")
            self.fp_output.delete("1.0", "end"); self.fp_output.insert("1.0", raw)
            self.status.set(self._tr("Manifest odcisku zapisany. Nie zawiera sekretnego klucza.", "Fingerprint manifest saved. It contains no secret key."))
        except (OSError, HelixProError) as exc: messagebox.showerror(self._tr("Odcisk klucza", "Key fingerprint"), str(exc))

    def _verify_fingerprint(self):
        try:
            if self.mode.get() == "password": raise HelixProError(self._tr("Wybierz tryb pliku-klucza.", "Select key-file mode."))
            path = filedialog.askopenfilename(title=self._tr("Wczytaj manifest", "Load manifest"), filetypes=[("JSON", "*.json")])
            if not path: return
            with open(path, encoding="utf-8") as f: fp = KeyFingerprint.from_dict(json.load(f))
            key = self._read_key()["key"]
            ok = verify_key_fingerprint(key, fp, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip())
            if ok:
                self.status.set(self._tr("Odcisk zgodny.", "Fingerprint matches."))
                messagebox.showinfo("Weryfikacja", self._tr("Klucz i kontekst pasują do manifestu. To nie jest dowód uprawnień.", "Key and context match the manifest. This does not prove authorization."))
            else:
                self.status.set(self._tr("Niezgodność odcisku.", "Fingerprint mismatch."))
                messagebox.showwarning("Weryfikacja", self._tr("Klucz lub identyfikator obiektu/klucza nie pasuje.", "Key or object/key ID does not match."))
        except (OSError, ValueError, HelixProError) as exc: messagebox.showerror(self._tr("Weryfikacja", "Verification"), str(exc))

    def _representation(self):
        path = filedialog.askopenfilename(title=self._tr("Wybierz szyfrogram", "Select ciphertext"))
        if not path: return
        try:
            value = representation_fingerprint_file(path)
            self.clipboard_clear(); self.clipboard_append(value)
            self.status.set(self._tr("Odcisk reprezentacji skopiowano do schowka: ", "Representation fingerprint copied: ") + value)
            messagebox.showinfo(self._tr("Odcisk szyfrogramu", "Ciphertext fingerprint"), value + "\n\nSkopiowano do schowka.")
        except HelixProError as exc: messagebox.showerror(self._tr("Odcisk szyfrogramu", "Ciphertext fingerprint"), str(exc))

    def _identity_manager(self):
        signer_path = self.signer_file.get().strip()
        if not signer_path or not os.path.isfile(signer_path): raise HelixProError(self._tr("Wybierz prywatny klucz podpisujący Ed25519 w formacie PEM.", "Select an Ed25519 private signing key in PEM format."))
        password = self.signer_password.get().encode("utf-8") if self.signer_password.get() else None
        with open(signer_path, "rb") as f: signer = serialization.load_pem_private_key(f.read(), password=password)
        if not isinstance(signer, Ed25519PrivateKey): raise HelixProError(self._tr("Klucz podpisujący musi być Ed25519.", "Signing key must be Ed25519."))
        lines = [x.strip() for x in self.anchors.get("1.0", "end").splitlines() if x.strip()]
        if len(lines) < 3: raise HelixProError(self._tr("Skonfiguruj co najmniej 3 niezależne endpointy quorum.", "Configure at least 3 independent quorum endpoints."))
        anchors = []
        for line in lines:
            parts = [x.strip() for x in line.split("|", 1)]
            if len(parts) != 2: raise HelixProError(self._tr("Każdy świadek musi mieć format HTTPS_URL | BEARER_TOKEN.", "Each witness must use HTTPS_URL | BEARER_TOKEN format."))
            anchors.append(HTTPTrustAnchor(parts[0], parts[1]))
        quorum = QuorumTrustAnchor(anchors)
        ledger = AIRPIntegrityLedger(self.ledger_path.get(), signer, trust_anchor=quorum)
        return AIRPIdentityManager(ledger)

    def _register_identity(self):
        try:
            if self.mode.get() == "password": raise HelixProError(self._tr("Rejestracja fingerprint wymaga pliku klucza.", "Fingerprint registration requires a key file."))
            key = self._read_key()["key"]
            manager = self._identity_manager()
            result = manager.register_key(key, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip())
            self.refresh_dashboard()
            if result.anchored:
                self.status.set(self._tr("AIRP: odcisk zakotwiczony w quorum.", "AIRP: fingerprint anchored by quorum."))
                messagebox.showinfo(self._tr("AIRP / Quorum", "AIRP / Quorum"), result.message)
            else:
                self.status.set(self._tr("AIRP: lokalny wpis oczekuje na quorum.", "AIRP: local event is waiting for quorum."))
                messagebox.showwarning(self._tr("AIRP / Quorum — pending", "AIRP / Quorum — pending"), result.message + "\n\nStatus: " + result.anchor_status)
        except (OSError, ValueError, TypeError, HelixProError) as exc: messagebox.showerror(self._tr("AIRP / Quorum", "AIRP / Quorum"), str(exc))

    def _rotate_identity(self):
        try:
            old_path = self.old_key_file.get().strip()
            if not old_path or not os.path.isfile(old_path):
                raise HelixProError(self._tr("Wskaż poprzedni plik klucza.", "Select the previous key file."))
            with open(old_path, "rb") as f: old_key = f.read(33)
            new_key = self._read_key()["key"]
            if len(old_key) != 32: raise HelixProError(self._tr("Poprzedni klucz musi mieć dokładnie 32 bajty.", "Previous key must be exactly 32 bytes."))
            manager = self._identity_manager()
            signer_path = self.signer_file.get().strip()
            password = self.signer_password.get().encode("utf-8") if self.signer_password.get() else None
            with open(signer_path, "rb") as f: signer = serialization.load_pem_private_key(f.read(), password=password)
            result = manager.rotate_key(
                old_key, new_key, object_id=self.object_id.get().strip(),
                old_key_id=self.old_key_id.get().strip(), new_key_id=self.key_id.get().strip(),
                signer=signer,
            )
            self.refresh_dashboard()
            if result.anchored:
                self.status.set(self._tr("AIRP: rotacja klucza potwierdzona przez quorum.", "AIRP: key rotation confirmed by quorum."))
                messagebox.showinfo(self._tr("AIRP / rotacja", "AIRP / rotation"), result.message)
            else:
                self.status.set(self._tr("AIRP: rotacja lokalna — oczekuje na quorum.", "AIRP: local rotation — waiting for quorum."))
                messagebox.showwarning(self._tr("AIRP / rotacja — pending", "AIRP / rotation — pending"), result.message + "\n\nStatus: " + result.anchor_status)
        except (OSError, ValueError, TypeError, HelixProError) as exc:
            messagebox.showerror(self._tr("AIRP / rotacja", "AIRP / rotation"), str(exc))

    def _verify_quorum(self):
        try:
            manager = self._identity_manager()
            result = manager.retry_anchor()
            self.refresh_dashboard()
            self.status.set(self._tr("AIRP status: ", "AIRP status: ") + result.status)
            messagebox.showinfo(self._tr("AIRP / Quorum", "AIRP / Quorum"), f"Status: {result.status}\nLokalna sekwencja: {result.local_sequence}\nZakotwiczona sekwencja: {result.anchored_sequence}")
        except (OSError, ValueError, HelixProError) as exc: messagebox.showerror(self._tr("AIRP / Quorum", "AIRP / Quorum"), str(exc))


def main():
    app = HelixLockApp()
    app.mainloop()


if __name__ == "__main__":
    main()
