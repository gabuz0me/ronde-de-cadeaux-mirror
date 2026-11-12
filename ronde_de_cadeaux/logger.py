"""Logging.

Permet à un éventuel autre script de se "brancher" sur les sorties de ronde-de-cadeaux
afin d'en faire quelque chose, sans avoir à écouter stdout et tout en ajoutant de la
sémantique sur l'information véhiculée.
"""

from __future__ import annotations

import os
import sys
from enum import Enum

from .tools import fill_dedent


class Logger:
    """Objet de base."""

    class Type(Enum):
        """Type de logging."""

        DEBUG = 0
        INFO = 1
        WARNING = 2
        ERROR = 3

    def __init__(self) -> None:
        self.show_debug = os.environ.get("RONDE_DE_CADEAUX_DEBUG") == "1"
        self.debug("!! Mode de débogage activé !!")

    def debug(self, msg: str, *, dedent: bool = True, newline: bool = True) -> None:  # noqa
        if self.show_debug:
            self._log(msg, Logger.Type.DEBUG, dedent=dedent, newline=newline)

    def info(self, msg: str, *, dedent: bool = True, newline: bool = True) -> None:  # noqa
        self._log(msg, Logger.Type.INFO, dedent=dedent, newline=newline)

    def warning(self, msg: str, *, dedent: bool = True, newline: bool = True) -> None:  # noqa
        self._log(msg, Logger.Type.WARNING, dedent=dedent, newline=newline)

    def error(self, msg: str, *, dedent: bool = True, newline: bool = True) -> None:  # noqa
        self._log(msg, Logger.Type.ERROR, dedent=dedent, newline=newline)

    def _log(self, msg: str, _type: Type, dedent: bool = True, newline: bool = True) -> None:
        color = ""
        output = sys.stdout
        _T = self.Type
        match _type:
            case _T.DEBUG:
                color = "\033[94m"  # Bleu
            case _T.INFO:
                color = ""  # Défaut
            case _T.WARNING:
                color = "\033[93m"  # Jaune
            case _T.ERROR:
                color = "\033[91m"  # Rouge
                output = sys.stderr
        if dedent:
            msg = fill_dedent(msg)
        print(f"{color}{msg}\033[0m", file=output, end="\n" if newline else "")


logger = Logger()
