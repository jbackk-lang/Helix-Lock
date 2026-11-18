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


def test_initial_locale_translations():
    assert translate("de", "Password") == "Passwort"
    assert translate("fr", "Password") == "Mot de passe"
    assert translate("es", "Password") == "Contraseña"
    assert translate("pt-BR", "Password") == "Senha"
    assert translate("ja", "Password") == "パスワード"
    assert translate("zh-CN", "Password") == "密码"
    assert translate("ko", "Password") == "비밀번호"
    assert translate("ja", "Untranslated security notice") == "Untranslated security notice"


def test_all_listed_languages_have_core_labels():
    for code in LANGUAGE_NAMES:
        assert translate(code, "Password", "Hasło")
        assert translate(code, "Files", "Pliki")
        assert translate(code, "Enter a password.", "Wpisz hasło.")


def test_regional_variants_use_parent_translation():
    assert translate("es-419", "Password") == translate("es", "Password")
    assert translate("en-US", "Password") == "Password"
    assert translate("pt", "Password") == "Palavra-passe"
    assert translate("uk", "Password") == "Пароль"
    assert translate("hi", "Password") == "पासवर्ड"
    assert translate("id", "Password") == "Kata sandi"
    assert translate("vi", "Password") == "Mật khẩu"
    assert translate("th", "Password") == "รหัสผ่าน"
