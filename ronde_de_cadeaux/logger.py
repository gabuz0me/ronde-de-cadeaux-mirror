"""Logging.

Permet à un éventuel autre script de se "brancher" sur les sorties de ronde-de-cadeaux
afin d'en faire quelque chose, sans avoir à écouter stdout et tout en ajoutant de la
sémantique sur l'information véhiculée.
"""

import logging
import os
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
    return "\033]8;{};{}\033\\{}\033]8;;\033\\".format(parameters, uri, text)
