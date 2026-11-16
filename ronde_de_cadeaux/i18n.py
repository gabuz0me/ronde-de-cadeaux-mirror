"""Le module de l'internationalisation."""

import gettext
from pathlib import Path

import i18nparse

_translation: gettext.NullTranslations = gettext.NullTranslations()


def set_language(lang: str | None = None) -> None:
    """Configure la langue utilisée par le programme.

    Utilise `lang` s'il est précisé, sinon se base sur la locale du système.

    Variable d'environnement :
    - `LANGUAGE` > `LC_ALL` > `LC_MESSAGES` > `LANG`
    """
    # https://www.gnu.org/software/gettext/manual/html_node/Locale-Environment-Variables.html
    global _translation
    _translation = gettext.translation(
        "messages",
        localedir=Path(__file__).parent / "locale/",
        languages=[lang] if lang else None,
        fallback=True,
    )
    i18nparse.activate(lang)


def _(message: str) -> str:
    """Traduit `message`."""
    return _translation.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Traduit `singular` ou `plural` selon `n`."""
    return _translation.ngettext(singular, plural, n)


# set_language()  # Initialise avec la langue par défaut
