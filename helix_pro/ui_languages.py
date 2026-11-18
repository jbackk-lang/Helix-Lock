"""Extensible desktop UI translations.

English is the stable message identifier. Polish remains the legacy source
translation until all strings are migrated into the catalogs. To add another
language, add its code to LANGUAGE_NAMES and translations to CATALOGS.
Missing entries fall back to English; never display mixed-language labels.
"""

LANGUAGE_NAMES = {"pl": "PL", "en": "EN"}
CATALOGS = {
    "en": {},
    "pl": {},
}


def translate(language: str, english: str, polish: str = "") -> str:
    """Translate one UI message, falling back to English for missing entries."""
    if language == "pl":
        return CATALOGS["pl"].get(english, polish or english)
    return CATALOGS.get(language, {}).get(english, english)
