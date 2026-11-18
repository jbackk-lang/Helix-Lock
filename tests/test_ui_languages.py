from helix_pro.ui_languages import (
    CATALOGS, LANGUAGE_NAMES, LANGUAGE_REGIONS, region_for_language, translate,
)


def test_region_registry_includes_three_continents():
    assert set(LANGUAGE_REGIONS) == {"Europa", "Ameryka", "Azja"}
    assert len(LANGUAGE_NAMES) >= 18
    assert region_for_language("ja") == "Azja"
    assert region_for_language("pt-BR") == "Ameryka"
    assert region_for_language("pl") == "Europa"


def test_polish_legacy_and_english_fallback():
    assert translate("pl", "Encrypt", "Szyfruj") == "Szyfruj"
    assert translate("ja", "Encrypt", "Szyfruj") == "Encrypt"
    assert translate("xx", "Encrypt", "Szyfruj") == "Encrypt"


def test_regional_catalog_fallback(monkeypatch):
    monkeypatch.setitem(CATALOGS, "pt", {"Encrypt": "Criptografar"})
    assert translate("pt-BR", "Encrypt", "Szyfruj") == "Criptografar"
    monkeypatch.setitem(CATALOGS, "pt-BR", {"Encrypt": "Criptografar arquivo"})
    assert translate("pt-BR", "Encrypt", "Szyfruj") == "Criptografar arquivo"
