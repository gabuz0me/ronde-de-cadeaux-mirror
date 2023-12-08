#!/usr/bin/env python3

"""

@author: Bertille Dubosc de Pesquidoux, Adrien Laporte, Adrian "Relex12" Bonnet, Vincent Menegaux

The purpose of this script is to determine a cycle of people which should
offer a present to the next one on the cycle and to inform them trough
an e-mail
"""

import datetime
import getpass
import json
import random
from yaml import safe_load, scanner
from src.graph_generation import generate_graph, Person, GraphGenerationException
from src.hamiltonian_path import hamilton, path_as_tuples
from src.logger import logger
from src.mail_sender import send_mails
from src.parser import parser


def pretty_print(graph):
    """Afficher joliment le graphe

    (debug en vrai)
    """
    logger.debug(json.dumps(graph, indent=2))


def ronde_cadeaux(data: dict,
                  show_path: bool = False,
                  output_file=None,
                  mail_auth: dict = None,
                  template_message: str = None,
                  no_imap: bool = False
                  ) -> None:
    """Routine principale

    `data` : données à partir desquelles construire un graphe
    `mail_auth` : configuration mail
    `message` : mail type
    `show_path` : afficher le chemin calculé
    """

    try:
        # Création du graphe
        graph = generate_graph(data)
    except GraphGenerationException as e:
        logger.error("Erreur dans la génération du graphe : " + e.message)
        return
    # pretty_print(graph)

    # Résolution du problème
    path = hamilton(graph, random.choice(list(graph)))
    if not path:
        logger.error("Pas de circuits trouvés, essayez d'amoindrir les contraintes.")
        return

    # Création des données pour affichage
    people_data = data['people']
    people_object_dict = {
        gifter_id : Person(gifter_id, people_data[gifter_id])
        for gifter_id in graph.keys()
    }
    gifter_giftee_tuple = path_as_tuples(path)

    # Création d'un résumé du tirage
    max_name_length = max(len(p.name) for p in people_object_dict.values()) # Aligner sur le nom le plus long
    draw = '\n'.join([
        f"{people_object_dict[gifter].name:>{max_name_length}} → {people_object_dict[giftee].name}"
        for gifter, giftee in gifter_giftee_tuple
    ])

    # Affichage éventuel
    if show_path:
        logger.output(draw)

    # Export éventuel dans un fichier texte
    if output_file:
        with output_file as f:
            f.write(f"Tirage du {datetime.datetime.now()} :\n")
            f.write(draw)
            f.write('\n\n')

    # Enfin envoi éventuel des mails
    if mail_auth:
        mail_auth['copy_to_sent_folder'] = not no_imap # = yes_imap :D
        send_mails(people_object_dict, gifter_giftee_tuple, mail_auth, template_message)


if __name__ == '__main__':
    # Parsing des arguments
    args = parser.parse_args()

    try:
        data = safe_load(args.FICHIER)
    except scanner.ScannerError:
        logger.error("Impossible de charger le fichier d'entrée : yaml invalide.")
        exit()

    mail_auth = None
    message = None
    if args.auth:
        try:
            mail_auth = safe_load(args.auth)
        except scanner.ScannerError:
            logger.error("Impossible de charger le fichier de configuration mail : yaml invalide.")
            exit()
        if not 'password' in mail_auth:
            mail_auth['password'] = getpass.getpass("Mot de passe mail :") # n'affiche pas ce qui est tapé

        message = args.message.read()

    # Exécution
    ronde_cadeaux(
        data=data,
        mail_auth=mail_auth,
        template_message=message,
        show_path=args.show,
        output_file=args.output,
        no_imap=args.no_imap,
    )
