"""
test_helix_pro_gui.py — testy logiki helix_pro_gui.py BEZ GUI (funkcje
na poziomie modułu: suggest_output_name, validate_output_path,
resolve_key_kwargs). Import tkinter jest celowo odłożony do wnętrza
_build_gui() w helix_pro_gui.py właśnie po to, żeby te testy działały
w środowisku bez wyświetlacza (jak to, w którym powstał ten plik) -
patrz docstring modułu.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helix_pro_gui import suggest_output_name, validate_output_path, resolve_key_kwargs
from helix_pro.cipher import generate_key


# ── suggest_output_name ──────────────────────────────────────────────

def test_suggest_output_name_appends_suffix_for_plain_file():
    assert suggest_output_name("/x/y/dane.txt") == "dane.txt.helixpro"


def test_suggest_output_name_strips_suffix_for_encrypted_file():
    assert suggest_output_name("/x/y/dane.txt.helixpro") == "dane.txt"


def test_suggest_output_name_case_insensitive_suffix_detection():
    assert suggest_output_name("/x/DANE.TXT.HELIXPRO") == "DANE.TXT"


def test_suggest_output_name_uses_basename_only():
    assert suggest_output_name("/bardzo/dlugi/sciezka/do/pliku.bin") == "pliku.bin.helixpro"


# ── validate_output_path ─────────────────────────────────────────────
# (Zastępuje dawne validate_paths(source, dest_dir, output_name) - teraz
# GUI dostaje PEŁNĄ ścieżkę wynikową z natywnego okna "Zapisz jako", nie
# składa jej z osobnego katalogu i nazwy - patrz _pick_output w GUI.)

def test_validate_output_path_rejects_missing_source(tmp_path):
    result = validate_output_path(str(tmp_path / "nieistnieje.txt"), str(tmp_path / "wynik.helixpro"))
    assert not result.ok
    assert "źródłow" in result.error


def test_validate_output_path_rejects_empty_output(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_text("x")
    result = validate_output_path(str(src), "")
    assert not result.ok
    assert "Zapisz jako" in result.error


def test_validate_output_path_rejects_output_in_nonexistent_directory(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_text("x")
    result = validate_output_path(str(src), str(tmp_path / "nieistnieje" / "wynik.helixpro"))
    assert not result.ok
    assert "Katalog docelowy" in result.error


def test_validate_output_path_rejects_output_identical_to_source(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_text("x")
    result = validate_output_path(str(src), str(src))
    assert not result.ok
    assert "tym samym plikiem" in result.error


def test_validate_output_path_accepts_valid_combination_in_same_directory(tmp_path):
    src = tmp_path / "dane.txt"
    src.write_text("x")
    result = validate_output_path(str(src), str(tmp_path / "wynik.helixpro"))
    assert result.ok
    assert result.output_path == str(tmp_path / "wynik.helixpro")


def test_validate_output_path_accepts_completely_different_directory(tmp_path):
    """Sedno pierwotnej prosby uzytkownika: dowolny katalog docelowy,
    niekoniecznie ten sam co zrodlo."""
    src_dir = tmp_path / "zrodlo"
    src_dir.mkdir()
    other_dir = tmp_path / "zupelnie" / "inny" / "katalog"
    other_dir.mkdir(parents=True)
    src = src_dir / "dane.txt"
    src.write_text("x")

    result = validate_output_path(str(src), str(other_dir / "wynik.helixpro"))
    assert result.ok
    assert result.output_path == str(other_dir / "wynik.helixpro")


# ── resolve_key_kwargs ────────────────────────────────────────────────

def test_resolve_key_kwargs_key_mode_reads_file(tmp_path):
    key = generate_key()
    key_path = tmp_path / "helix.key"
    key_path.write_bytes(key)
    result = resolve_key_kwargs("key", str(key_path), "")
    assert result.ok
    assert result.kwargs == {"key": key}


def test_resolve_key_kwargs_key_mode_rejects_missing_file(tmp_path):
    result = resolve_key_kwargs("key", str(tmp_path / "brak.key"), "")
    assert not result.ok


def test_resolve_key_kwargs_key_mode_rejects_wrong_size_key(tmp_path):
    bad_key_path = tmp_path / "zly.key"
    bad_key_path.write_bytes(b"za krotki")
    result = resolve_key_kwargs("key", str(bad_key_path), "")
    assert not result.ok
    assert "oczekiwano 32" in result.error


def test_resolve_key_kwargs_password_mode():
    result = resolve_key_kwargs("password", "", "tajne-haslo")
    assert result.ok
    assert result.kwargs == {"password": "tajne-haslo"}


def test_resolve_key_kwargs_password_mode_rejects_empty():
    result = resolve_key_kwargs("password", "", "")
    assert not result.ok


def test_resolve_key_kwargs_unknown_mode():
    result = resolve_key_kwargs("cos-innego", "", "")
    assert not result.ok


# ── integracja: cały przepływ bez GUI, przez encrypt_file/decrypt_file ──

def test_full_flow_key_mode_encrypt_then_decrypt_to_different_directory(tmp_path):
    """Dokladnie to, o co prosil uzytkownik: dowolny plik zrodlowy,
    zaszyfrowany do jednego katalogu, odszyfrowany do INNEGO katalogu -
    bez uruchamiania GUI, przez te same funkcje co przyciski Szyfruj/Deszyfruj."""
    from helix_pro.cipher import encrypt_file, decrypt_file

    src_dir = tmp_path / "zrodlo"
    enc_dir = tmp_path / "zaszyfrowane"
    dec_dir = tmp_path / "odszyfrowane"
    for d in (src_dir, enc_dir, dec_dir):
        d.mkdir()

    src = src_dir / "dane.txt"
    src.write_bytes(b"tresc do ochrony przez GUI")
    key_path = tmp_path / "helix.key"
    key_path.write_bytes(generate_key())
    key_result = resolve_key_kwargs("key", str(key_path), "")
    assert key_result.ok

    enc_output = str(enc_dir / suggest_output_name(str(src)))
    enc_validation = validate_output_path(str(src), enc_output)
    assert enc_validation.ok
    encrypt_file(str(src), enc_validation.output_path, **key_result.kwargs)
    assert os.path.isfile(enc_validation.output_path)
    assert enc_validation.output_path != str(src)

    dec_output = str(dec_dir / suggest_output_name(enc_validation.output_path))
    dec_validation = validate_output_path(enc_validation.output_path, dec_output)
    assert dec_validation.ok
    decrypt_file(enc_validation.output_path, dec_validation.output_path, **key_result.kwargs)

    assert dec_validation.output_path == str(dec_dir / "dane.txt")
    assert open(dec_validation.output_path, "rb").read() == src.read_bytes()
