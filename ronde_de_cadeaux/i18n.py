"""Le module de l'internationalisation."""

import gettext
import locale
import os
import subprocess
import sys
from pathlib import Path

import i18nparse

from .logger import logger

_translation: gettext.NullTranslations = gettext.NullTranslations()
_SUPPORTED_LANGUAGES = ["en", "fr"]  # le premier élément EST LA LANGUE PAR DÉFAUT
_DEFAULT_LANGUAGE = _SUPPORTED_LANGUAGES[0]


def set_app_language(lang: str) -> None:
    """Configure la langue utilisée par le programme."""
    global _translation
    _translation = gettext.translation(
        "messages",
        localedir=Path(__file__).parent / "locale/",
        languages=[lang] if lang else None,
        fallback=True,
    )
    i18nparse.activate(lang)


def _process_language(lang: str) -> str:
    global _SUPPORTED_LANGUAGES, _DEFAULT_LANGUAGE
    _returned = _DEFAULT_LANGUAGE
    lang_nor = lang.lower()
    if len(lang_nor) > 2:
        lang_nor = lang_nor[0:2]
        if lang_nor in _SUPPORTED_LANGUAGES:
            _returned = lang_nor
    logger.debug(f"_process_language({lang}) -> '{lang_nor}' -> '{_returned}'")
    return _returned


# https://stackoverflow.com/a/25691701
# https://www.gnu.org/software/gettext/manual/html_node/Locale-Environment-Variables.html
# https://docs.python.org/fr/3/library/locale.html#locale.getdefaultlocale
def find_user_language() -> str:
    """Trouve la langue à utiliser pour l'affichage et les traductions.

    Renvoie un code de deux lettres.

    Comme `locale.getdefaultlocale()` est *deprecated* mais que `locale.getlocale()`
    ne fonctionne pas tout le temps sur Android, on fait à la mano.

    C'est si compliqué jpp merci stackoverflow et tout.
    """
    global _DEFAULT_LANGUAGE
    logger.debug("find_user_language()")
    if lang := os.environ.get("RONDE_LANG", None):
        logger.debug(f"RONDE_LANG: {lang}")
        return _process_language(lang)

    platform = sys.platform
    if platform == "win32":
        import ctypes

        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        lang = locale.windows_locale.get(lang_id, None)
        logger.debug(f"windows : {lang}")
        return _process_language(lang) if lang else _DEFAULT_LANGUAGE
    elif platform == "android":
        try:
            res = subprocess.run(["/system/bin/getprop", "persist.sys.locale"], capture_output=True, text=True)
        except Exception as e:
            logger.debug("android failed")
            logger.debug(e)
        else:
            lang = res.stdout.strip()
            logger.debug(f"android : {lang}")
            if lang:
                return _process_language(lang)

    locale.setlocale(locale.LC_ALL, "")
    lang, __ = locale.getlocale()
    logger.debug(f"locale.getlocale : {lang}")
    return _process_language(lang) if lang else _DEFAULT_LANGUAGE


def _(message: str) -> str:
    """Traduit `message`."""
    return _translation.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Traduit `singular` ou `plural` selon `n`."""
    return _translation.ngettext(singular, plural, n)
