"""Module illégal pour franciser argparse, faute de mieux."""

import gettext

__TRANSLATIONS = {
    "can't open '%(filename)s': %(error)s": "impossible d'ouvrir '%(filename)s'",
    "expected one argument": "un argument est nécessaire",
    "options": "Arguments optionnels",
    "positional arguments": "Arguments positionnels",
    "show this help message and exit": "Afficher ce message et quitter",
    "the following arguments are required: %s": "les arguments suivants sont nécessaires : %s",
    "unrecognized arguments: %s": "argument non reconnu: %s",
    "usage: ": "Utilisation : ",
    "%(prog)s: error: %(message)s\n": "%(prog)s: erreur: %(message)s\n",
}


def _translate(val: str) -> str:
    # print(val) # debug
    return __TRANSLATIONS.get(val, val)


def convert_argparse_to_french() -> None:
    """Convertit argparse en bon françois."""
    gettext.gettext = _translate


# Merci à Frederic dans https://stackoverflow.com/a/58602800
