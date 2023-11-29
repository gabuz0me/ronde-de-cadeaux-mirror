#!/usr/bin/env python3

"""

@author: Bertille Dubosc de Pesquidoux, Adrien Laporte, Adrian "Relex12" Bonnet

The purpose of this script is to determine a cycle of people which should
offer a present to the next one on the cycle and to inform them trough
an e-mail
"""

import datetime
import getpass
import json
import random
from yaml import safe_load, scanner
from lib.graph_generation import generate_graph, giftee
from lib.hamiltonian_path import hamilton
from lib.mail_sender import send_mails
from lib.parser import parser


def pretty_print(graph):
    """Afficher joliment le graphe

    (debug en vrai)"""
    graph_values_as_list = {
        key: list(value)
        for (key, value) in graph.items()
    }
    print(json.dumps(graph_values_as_list, indent=2))


def ronde_cadeaux(data: dict,
                  show_path: bool = False,
                  output_file=None,
                  mail_auth: dict = None,
                  message: str = None,
                  ) -> None:
    """Routine principale

    `data` : données à partir desquelles construire un graphe
    `mail_auth` : configuration mail
    `message` : mail type
    `show_path` : afficher le chemin calculé
    """

    # Création du graphe
    graph = generate_graph(data)
    # pretty_print(graph)

    # Résolution du problème
    path = hamilton(graph, random.choice(list(graph)), [])
    if not path:
        print("Pas de circuits trouvés, essayez d'amoindrir les contraintes.")
        exit()

    # Création d'un résumé du tirage
    max_name_length = max(len(p) for p in path)
    draw = '\n'.join([
        f"{person:>{max_name_length}} → {giftee(path, person)}"
        for person in path
    ])

    # Affichage éventuel
    if show_path:
        print(draw)

    # Export éventuel dans un fichier texte
    if output_file:
        with output_file as f:
            f.write(f"Tirage du {datetime.datetime.now()} :\n")
            f.write(draw)
            f.write('\n\n')

    # Enfin envoi éventuel des mails
    if mail_auth:
        send_mails(data["people"], path, mail_auth, message)


if __name__ == '__main__':
    # Parsing des arguments
    args = parser.parse_args()

    try:
        data = safe_load(args.file)
    except scanner.ScannerError:
        print("Impossible de charger le fichier d'entrée : yaml invalide.")
        exit()

    mail_auth = None
    message = None
    if args.auth:
        try:
            mail_auth = safe_load(args.auth)
        except scanner.ScannerError:
            print(
                "Impossible de charger le fichier de configuration mail : yaml invalide.")
            exit()
        if not 'password' in mail_auth:
            mail_auth['password'] = getpass.getpass("Mot de passe mail :") # n'affiche pas ce qui est tapé

        message = args.message.read()

    # Exécution
    ronde_cadeaux(
        data=data,
        mail_auth=mail_auth,
        message=message,
        show_path=args.show,
        output_file=args.output,
    )
