"""Logging.

Permet à un éventuel autre script de se "brancher" sur les sorties de ronde-de-cadeaux
afin d'en faire quelque chose, sans avoir à écouter stdout et tout en ajoutant de la
sémantique sur l'information véhiculée.
"""

from __future__ import annotations

import sys
from enum import Enum
from typing import Callable


class Logger:
    """Objet de base."""

    class Type(Enum):
        """Type de logging."""

        DEBUG = 0
        INFO = 1
        OUTPUT = 2
        ERROR = 3

    def __init__(self, printer: Printer) -> None:
        self.printer = printer

    def info(self, msg: str) -> None:  # noqa
        self.printer(msg, Logger.Type.INFO)

    def debug(self, msg: str) -> None:  # noqa
        self.printer(msg, Logger.Type.DEBUG)

    def output(self, msg: str) -> None:  # noqa
        self.printer(msg, Logger.Type.OUTPUT)

    def error(self, msg: str) -> None:  # noqa
        self.printer(msg, Logger.Type.ERROR)


def _default_printer(msg: str, type: Logger.Type) -> None:
    output = sys.stdout
    if type == Logger.Type.DEBUG:
        color = "\033[94m"  # Bleu
    elif type == Logger.Type.INFO:
        color = ""  # Défaut
    elif type == Logger.Type.OUTPUT:
        color = "\033[92m"  # Vert
    elif type == Logger.Type.ERROR:
        color = "\033[91m"  # Rouge
        output = sys.stderr
    print(f"{color}{msg}\033[0m", file=output)


Printer = Callable[[str, Logger.Type], None]

logger = Logger(_default_printer)
