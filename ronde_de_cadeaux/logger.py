"""Logging.

Permet à un éventuel autre script de se "brancher" sur les sorties de ronde-de-cadeaux
afin d'en faire quelque chose, sans avoir à écouter stdout et tout en ajoutant de la
sémantique sur l'information véhiculée.
"""

import logging
import os
import sys
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
