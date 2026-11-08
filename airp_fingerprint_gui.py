#!/usr/bin/env python3
"""AIRP Key Fingerprint — visual desktop companion for Helix-Lock."""
from __future__ import annotations

import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from helix_pro.airp_key_fingerprint import (
    KeyFingerprint,
    create_key_fingerprint,
    representation_fingerprint_file,
    verify_key_fingerprint,
)
from helix_pro.cipher import HelixProError

BG = "#101827"
PANEL = "#182437"
ACCENT = "#54D6A0"
TEXT = "#F2F6FC"
MUTED = "#9FB0C5"
WARNING = "#F6C76A"


class FingerprintGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Helix-Lock · AIRP Fingerprint")
        self.geometry("900x720")
        self.minsize(760, 620)
        self.configure(bg=BG)
        self.key_path = tk.StringVar()
        self.manifest_path = tk.StringVar()
        self.object_id = tk.StringVar(value="my-document")
        self.key_id = tk.StringVar(value="key-v1")
        self.status = tk.StringVar(value="Wybierz plik klucza, aby rozpocząć.")
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TEntry", fieldbackground="#24344B", foreground=TEXT, insertcolor=TEXT)
        style.configure("TButton", padding=8, font=("Segoe UI", 10))
        style.configure("Accent.TButton", background=ACCENT, foreground="#0D1A25", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED)
        style.configure("TLabelframe", background=PANEL, foreground=TEXT)
        style.configure("TLabelframe.Label", background=PANEL, foreground=ACCENT, font=("Segoe UI", 11, "bold"))

    def _card(self, parent, title, subtitle):
        frame = tk.Frame(parent, bg=PANEL, highlightbackground="#2A3B53", highlightthickness=1)
        tk.Label(frame, text=title, bg=PANEL, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
        tk.Label(frame, text=subtitle, bg=PANEL, fg=MUTED, font=("Segoe UI", 9), wraplength=760, justify="left").pack(anchor="w", padx=16, pady=(0, 12))
        return frame

    def _build(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=22, pady=(18, 8))
        self._draw_hero(header)
        tk.Label(header, text="AIRP KEY FINGERPRINT", bg=BG, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=(100, 0), pady=(8, 0))
        tk.Label(header, text="Tożsamość klucza · kontrola zgodności · historia rotacji", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=(101, 0))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=10)

        identity = self._card(body, "01  Tożsamość klucza", "Odcisk jest powiązany z identyfikatorem obiektu i klucza. Klucz pozostaje lokalny — nie jest zapisywany w manifeście.")
        identity.pack(fill="x", pady=6)
        row = tk.Frame(identity, bg=PANEL); row.pack(fill="x", padx=16, pady=4)
        tk.Label(row, text="Plik klucza", bg=PANEL, fg=MUTED, width=14, anchor="w").pack(side="left")
        ttk.Entry(row, textvariable=self.key_path).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(row, text="Wybierz…", command=self._pick_key).pack(side="left")
        for label, var in (("ID obiektu", self.object_id), ("ID klucza", self.key_id)):
            row = tk.Frame(identity, bg=PANEL); row.pack(fill="x", padx=16, pady=4)
            tk.Label(row, text=label, bg=PANEL, fg=MUTED, width=14, anchor="w").pack(side="left")
            ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)

        actions = tk.Frame(identity, bg=PANEL); actions.pack(fill="x", padx=16, pady=(8, 14))
        ttk.Button(actions, text="✦ Utwórz odcisk", style="Accent.TButton", command=self._create).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="✓ Zweryfikuj odcisk", command=self._verify).pack(side="left")

        fp = self._card(body, "02  Odcisk kryptograficzny", "Manifest zawiera algorytm, kontekst i wartość odcisku — nigdy klucz ani hasło.")
        fp.pack(fill="x", pady=6)
        self.fingerprint = tk.Text(fp, height=4, bg="#0C1421", fg=ACCENT, insertbackground=TEXT, relief="flat", wrap="word", font=("Consolas", 10))
        self.fingerprint.pack(fill="x", padx=16, pady=(0, 14))
        self.fingerprint.insert("1.0", "Tutaj pojawi się odcisk po utworzeniu lub wczytaniu manifestu.")
        self.fingerprint.configure(state="disabled")

        rep = self._card(body, "03  Odcisk reprezentacji", "Niezależny SHA-256 wskazuje konkretny plik szyfrogramu. Zmiana choćby jednego bajtu daje inny odcisk.")
        rep.pack(fill="x", pady=6)
        row = tk.Frame(rep, bg=PANEL); row.pack(fill="x", padx=16, pady=(0, 14))
        ttk.Button(row, text="Oblicz odcisk pliku szyfrogramu…", command=self._representation).pack(side="left")
        self.rep_value = tk.StringVar(value="Nie obliczono")
        tk.Label(row, textvariable=self.rep_value, bg=PANEL, fg=ACCENT, font=("Consolas", 9), wraplength=520, justify="left").pack(side="left", padx=12)

        status = tk.Frame(self, bg="#0C1421")
        status.pack(fill="x", side="bottom")
        self.status_label = tk.Label(status, textvariable=self.status, bg="#0C1421", fg=MUTED, anchor="w", padx=18, pady=12, font=("Segoe UI", 10))
        self.status_label.pack(fill="x")

    def _draw_hero(self, parent):
        canvas = tk.Canvas(parent, width=82, height=78, bg=BG, highlightthickness=0)
        canvas.place(x=0, y=0)
        canvas.create_oval(12, 8, 66, 62, outline=ACCENT, width=2)
        canvas.create_oval(24, 20, 54, 50, outline="#8BC8FF", width=2)
        canvas.create_line(39, 35, 39, 72, fill=ACCENT, width=3)
        canvas.create_line(39, 58, 53, 58, fill=ACCENT, width=3)
        canvas.create_line(39, 66, 49, 66, fill=ACCENT, width=3)
        canvas.create_oval(33, 29, 45, 41, fill=ACCENT, outline="")

    def _set_text(self, value):
        self.fingerprint.configure(state="normal")
        self.fingerprint.delete("1.0", "end")
        self.fingerprint.insert("1.0", value)
        self.fingerprint.configure(state="disabled")

    def _read_key(self):
        path = self.key_path.get().strip()
        if not path or not os.path.isfile(path):
            raise HelixProError("Wskaż istniejący plik klucza.")
        with open(path, "rb") as stream:
            key = stream.read(33)
        if len(key) != 32:
            raise HelixProError("Klucz musi mieć dokładnie 32 bajty.")
        if not self.object_id.get().strip() or not self.key_id.get().strip():
            raise HelixProError("Uzupełnij ID obiektu i ID klucza.")
        return key

    def _pick_key(self):
        path = filedialog.askopenfilename(title="Wybierz 32-bajtowy plik klucza")
        if path:
            self.key_path.set(path)
            self.status.set("Wybrano plik. Klucz zostanie odczytany lokalnie.")
    
    def _create(self):
        try:
            key = self._read_key()
            fp = create_key_fingerprint(key, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip())
            manifest = json.dumps(fp.to_dict(), indent=2, ensure_ascii=False)
            self._set_text(manifest)
            target = filedialog.asksaveasfilename(
                title="Zapisz publiczny manifest odcisku", defaultextension=".json",
                initialfile="airp-key-fingerprint.json",
                filetypes=[("JSON", "*.json")],
            )
            if target:
                with open(target, "x", encoding="utf-8") as stream:
                    stream.write(manifest + "\n")
                self.status.set("Odcisk utworzony i zapisany. Klucz nie opuścił komputera.")
            else:
                self.status.set("Odcisk utworzony w pamięci. Nie zapisano manifestu.")
        except FileExistsError:
            messagebox.showerror("Plik istnieje", "Wybierz inną nazwę manifestu — istniejący plik nie został nadpisany.")
        except (OSError, HelixProError) as exc:
            messagebox.showerror("Nie udało się utworzyć odcisku", str(exc))

    def _load_manifest(self):
        path = filedialog.askopenfilename(title="Wczytaj manifest AIRP", filetypes=[("JSON", "*.json")])
        if not path:
            return None
        with open(path, "r", encoding="utf-8") as stream:
            data = json.load(stream)
        fp = KeyFingerprint.from_dict(data)
        self._set_text(json.dumps(fp.to_dict(), indent=2, ensure_ascii=False))
        self.manifest_path.set(path)
        return fp

    def _verify(self):
        try:
            fp = self._load_manifest()
            if fp is None:
                return
            key = self._read_key()
            valid = verify_key_fingerprint(
                key, fp, object_id=self.object_id.get().strip(), key_id=self.key_id.get().strip()
            )
            if valid:
                self.status.set("ZGODNOŚĆ POTWIERDZONA — klucz i kontekst pasują do manifestu.")
                self.status_label.configure(fg=ACCENT)
                messagebox.showinfo("AIRP · zgodność", "Odcisk pasuje. To potwierdza zgodność klucza z manifestem, nie jego uprawnienia.")
            else:
                self.status.set("NIEZGODNOŚĆ — klucz lub kontekst nie pasuje.")
                self.status_label.configure(fg="#FF7B7B")
                messagebox.showwarning("AIRP · niezgodność", "Klucz lub identyfikator obiektu/klucza nie pasuje do manifestu.")
        except (OSError, ValueError, json.JSONDecodeError, HelixProError) as exc:
            messagebox.showerror("Błąd weryfikacji", str(exc))

    def _representation(self):
        path = filedialog.askopenfilename(title="Wybierz plik szyfrogramu")
        if not path:
            return
        try:
            self.rep_value.set(representation_fingerprint_file(path))
            self.status.set("Obliczono odcisk reprezentacji szyfrogramu.")
        except (OSError, HelixProError) as exc:
            messagebox.showerror("Błąd pliku", str(exc))


if __name__ == "__main__":
    FingerprintGUI().mainloop()
