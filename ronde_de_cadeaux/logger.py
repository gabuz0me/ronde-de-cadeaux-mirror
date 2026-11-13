"""Logging.

Permet à un éventuel autre script de se "brancher" sur les sorties de ronde-de-cadeaux
afin d'en faire quelque chose, sans avoir à écouter stdout et tout en ajoutant de la
sémantique sur l'information véhiculée.
"""

import logging
import sys
from typing import override

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


def set_logger_level(verbosity: int, quiet: bool) -> None:
    """En fonction des arguments du parser, ajuste le niveau du logger."""
    assert not (verbosity and quiet)
    if quiet:
        logger.setLevel(logging.ERROR)
        return

    match verbosity:
        case 0:
            logger.setLevel(logging.WARNING)  # Cas par défaut
        case 1:
            logger.setLevel(logging.INFO)
        case _:
            logger.setLevel(logging.DEBUG)

    if verbosity > 2:
        logger.warning("La verbosité ne va pas plus loin que -vv.")
