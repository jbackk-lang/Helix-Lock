"""Regional language registry for the desktop interface.

Regions organize the selector; they never restrict which language may be used.
Untranslated messages fall back to English. A language appearing in the menu
is not a claim that a complete translation exists.
"""

LANGUAGE_REGIONS = {
    "Europa": {
        "pl": "Polski", "en": "English", "de": "Deutsch",
        "fr": "Français", "es": "Español", "it": "Italiano",
        "pt": "Português", "uk": "Українська",
    },
    "Ameryka": {
        "en-US": "English (US)", "es-419": "Español (Latinoamérica)",
        "pt-BR": "Português (Brasil)",
    },
    "Azja": {
        "zh-CN": "简体中文", "ja": "日本語", "ko": "한국어",
        "hi": "हिन्दी", "id": "Bahasa Indonesia",
        "vi": "Tiếng Việt", "th": "ไทย",
    },
}
LANGUAGE_NAMES = {
    code: name for languages in LANGUAGE_REGIONS.values()
    for code, name in languages.items()
}
# Translation catalogs are deliberately separate from available language codes.
# Populate each catalog with reviewed strings before marking a locale complete.
CATALOGS = {"en": {}, "pl": {}}
LANGUAGE_FALLBACKS = {"en-US": "en", "es-419": "es", "pt-BR": "pt"}


def region_for_language(language: str) -> str:
    for region, languages in LANGUAGE_REGIONS.items():
        if language in languages:
            return region
    return "Europa"


def translate(language: str, english: str, polish: str = "") -> str:
    """Return reviewed translation or English fallback; never join languages."""
    if language == "pl":
        return CATALOGS["pl"].get(english, polish or english)
    catalog = CATALOGS.get(language, {})
    if english in catalog:
        return catalog[english]
    base = LANGUAGE_FALLBACKS.get(language)
    if base and english in CATALOGS.get(base, {}):
        return CATALOGS[base][english]
    return english
