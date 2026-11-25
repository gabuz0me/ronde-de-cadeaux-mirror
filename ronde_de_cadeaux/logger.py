"""Logging ET fonctions-outils qui touchent au texte (couleur).

Permet à un éventuel autre script de se "brancher" sur les sorties de ronde-de-cadeaux
afin d'en faire quelque chose, sans avoir à écouter stdout et tout en ajoutant de la
sémantique sur l'information véhiculée.
"""

import logging
import os
import re
import sys
from enum import IntEnum
from typing import NamedTuple, override

import colorlog

from .tools import fill_dedent


class _FillDedentFormatter(colorlog.ColoredFormatter):
    @override
    def formatMessage(self, record: logging.LogRecord) -> str:
        record.message = fill_dedent(record.message)
        return super().formatMessage(record)


logger = colorlog.getLogger("ronde")
handler = colorlog.StreamHandler(sys.stderr)
handler.setFormatter(
    _FillDedentFormatter(
        "%(log_color)s%(message)s%(reset)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
        },
    )
)

logger.addHandler(handler)

VerboseQuiet = NamedTuple("VerboseQuiet", [("verbose", bool), ("quiet", bool)])


def set_logger_level(verbose_quiet: VerboseQuiet | None = None) -> None:
    """En fonction des arguments du parser et de la variable d'environnement `RONDE_DEBUG`, ajuste le niveau du logger."""
    global logger
    if os.environ.get("RONDE_DEBUG", "0") != "0":
        logger.setLevel(logging.DEBUG)
    elif verbose_quiet:
        assert not (verbose_quiet.verbose and verbose_quiet.quiet)
        if verbose_quiet.verbose:
            logger.setLevel(logging.INFO)
        elif verbose_quiet.quiet:
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.WARNING)  # Cas par défaut


# https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007
class Color(IntEnum):
    """Couleur du texte si `NO_COLOR` n'est pas présente dans l'environnement."""

    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    CYAN = 36


class Style(IntEnum):
    """Style du texte si `NO_COLOR` n'est pas présente dans l'environnement."""

    NORMAL = 0
    BOLD = 1
    ITALIC = 3
    UNDERLINE = 4
    NEGATIVE = 7
    CROSSED = 9


def colored(text: str, color: Color, style: Style = Style.NORMAL) -> str:
    """Colore le texte."""
    if os.environ.get("NO_COLOR", "0") != "0":
        return text
    return f"\033[{style};{color}m{text}\033[0m"


# https://stackoverflow.com/a/71309268
def as_link(uri: str, text: str | None = None) -> str:
    R"""Lien dans le terminal \o/."""
    if text is None:
        text = uri
    if os.environ.get("NO_COLOR", "0") != "0":
        return text
    parameters = ""
    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    return f"\033]8;{parameters};{uri}\033\\{text}\033]8;;\033\\"


_ANSI_BEGIN_COLOR = r"\033\[[0-9;]*m"
_ANSI_BEGIN_URI = r"\033\]8;[0-9]*;[^\033]*\033\\"
_ANSI_ESCAPE = re.compile(f"{_ANSI_BEGIN_COLOR}|{_ANSI_BEGIN_URI}")


def capitalize(text: str) -> str:
    """Comme `text.capitalize()`, mais seulement sur la première lettre, en ignorant les codes ANSI en tête.

    Passé trop de temps dessus :(
    """
    # 1. On avance tant qu'on peut match un lien ou une couleur, c'est là qu'on a la possibilité de mettre un majuscule
    pos = 0
    while match := _ANSI_ESCAPE.match(text, pos):
        pos = match.end()

    # 2. Si on a avancé jusqu'au bout et que soit on dépasse (pas de texte, juste la couleur) ou qu'on n'a pas de lettre
    if pos >= len(text) or not text[pos].isalpha():
        return text

    # 3. Ça majusculise
    return text[:pos] + text[pos].upper() + text[pos + 1 :]
