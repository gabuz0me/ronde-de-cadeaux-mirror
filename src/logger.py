from enum import Enum

""""
Permet à un éventuel autre script de se "brancher" sur les sorties de ronde-de-cadeaux
afin d'en faire quelque chose, sans avoir à écouter stdout et tout en ajoutant de la
sémantique sur l'information véhiculée.
"""

class Logger:
    class Type(Enum):
        DEBUG = 0
        INFO = 1
        OUTPUT = 2
        ERROR = 3

    def __init__(self, printer):
        self.printer = printer

    def info(self, msg: str):
        self.printer(msg, Logger.Type.INFO)

    def debug(self, msg: str):
        self.printer(msg, Logger.Type.DEBUG)

    def output(self, msg: str):
        self.printer(msg, Logger.Type.OUTPUT)

    def error(self, msg: str):
        self.printer(msg, Logger.Type.ERROR)


def _default_printer(msg: str, type: Logger.Type):
    if   type == Logger.Type.DEBUG:  color = '\033[94m' # Bleu
    elif type == Logger.Type.INFO:   color = ''         # Défaut
    elif type == Logger.Type.OUTPUT: color = '\033[92m' # Vert
    elif type == Logger.Type.ERROR:  color = '\033[91m' # Rouge
    print(f"{color}{msg}\033[0m")


logger = Logger(_default_printer)