#!/usr/bin/env python3

"""

@author: Bertille Dubosc de Pesquidoux, Adrian "Relex12" Bonnet

The purpose of this script is to determine a cycle of people which should
offer a present to the next one on the cycle and to inform them trough
an e-mail
"""

from yaml import safe_load, scanner
from textwrap import dedent
import argparse
import random
from lib.graph_generation import graph_gen
from lib.hamiltonian_path import hamilton
from lib.mail_sender import send_mails


class ImpossibleToDrawError(Exception):
    """
    This error is raised when `nb_err` exceeds `LIMIT_ERR_MAX`.
    """


def makeParser() -> argparse.ArgumentParser:
    """Fabrique et retourne le parser des arguments"""
    parser = argparse.ArgumentParser(
        description=dedent("""\
            Ce programme permet de générer un tirage de gens à qui offrir
            des cadeaux en prenant en compte un système de contraintes
            complexes. Si un chemin hamiltonien est trouvé, un mail est
            envoyé à chacun⋅e des participant⋅e⋅s leur indiquant à qui
            offrir un présent.
            """
                           ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-f', '--file',
        type=argparse.FileType('r'),
        help='Fichier yaml à parser',
        required=True,
    )

    parser.add_argument(
        '-a', '--auth',
        type=argparse.FileType('r'),
        help='Fichier de configuration mail',
        required=True,
    )

    parser.add_argument(
        '-m', '--message',
        type=argparse.FileType('r'),
        help='Fichier mail type',
        default=DEFAULT_MAIL_TEMPLATE,
    )

    return parser


# When too many errors occur during the drawing, it is considered impossible.
LIMIT_ERR_MAX = 10
DEFAULT_MAIL_TEMPLATE = 'message.txt'


def ronde_cadeaux(data: dict, mail_auth: dict, message: str) -> None:
    """Routine principale

    `data` : données à partir desquelles construire un graphe
    `mail_auth` : configuration mail
    `message` : mail type
    """
    graph = graph_gen(data)

    drawable = False
    nb_err = 0
    while not drawable:
        path = hamilton(graph, len(graph), random.choice(list(graph)), [])
        if path is None:
            nb_err += 1
            print("Erreur")
        else:
            drawable = True
        if nb_err > LIMIT_ERR_MAX:
            print("Pas de circuits trouvés, essayez d'amoindrir les contraintes.")
            raise ImpossibleToDrawError

    with open('circuit.txt', 'w') as f:
        # on sauvegarde le circuit obtenu dans un fichier au cas où ça planterait
        # quelque part au milieu de l'envoi de mails, pour ne pas se retrouver avec
        # un tirage incomplet
        f.write(str(path))

    send_mails(data["people"], path, mail_auth, message)


if __name__ == '__main__':
    # Parsing des arguments
    args = makeParser().parse_args()

    try:
        data = safe_load(args.file)
    except scanner.ScannerError:
        print("Impossible de charger le fichier d'entrée : yaml invalide.")
        exit()

    try:
        mail_auth = safe_load(args.auth)
    except scanner.ScannerError:
        print("Impossible de charger le fichier de configuration mail : yaml invalide.")
        exit()

    message = args.message.read()

    # Exécution
    ronde_cadeaux(data, mail_auth, message)
