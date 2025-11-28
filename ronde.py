#!/usr/bin/env python3

"""
@author: Adrien Laporte, Bertille Dubosc de Pesquidoux, Adrian "Relex12" Bonnet, Vincent Menegaux

The purpose of this script is to determine a cycle of people which should
offer a present to the next one on the cycle and to inform them trough
an e-mail
"""  # noqa

import datetime
import json
import random
from argparse import Namespace

from yaml import safe_load, scanner

from src.graph_generation import GraphGenerationException, Person, generate_graph
from src.hamiltonian_path import hamilton, path_as_tuples
from src.logger import logger
from src.mail_sender import mail_data_to_mail_info, send_mails, test_mail_sending
from src.parser import parser


def pretty_print(graph: dict) -> None:
    """Afficher joliment le graphe.

    (debug en vrai)
    """
    logger.debug(json.dumps(graph, indent=2))


def ronde_cadeaux(
    args: Namespace,
    data: dict,
    mail_data: dict | None = None,
) -> None:
    """Routine principale."""
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
    people_data = data["people"]
    people_object_dict = {gifter_id: Person(gifter_id, people_data[gifter_id]) for gifter_id in graph.keys()}
    gifter_giftee_tuple = path_as_tuples(people_object_dict, path)

    # Création d'un résumé du tirage
    max_name_length = max(len(p.name) for p in people_object_dict.values())  # Aligner sur le nom le plus long
    draw = "\n".join([f"{gifter.name:>{max_name_length}} → {giftee.name}" for gifter, giftee in gifter_giftee_tuple])

    # Affichage éventuel
    if args.show:
        logger.output(draw)

    # Export éventuel dans un fichier texte
    if args.output:
        with args.output as f:
            f.write(f"Tirage du {datetime.datetime.now().replace(microsecond=0)} :\n")
            f.write(draw)
            f.write("\n\n")

    # Enfin envoi éventuel des mails
    if mail_data:
        mail_data["copy_to_sent_folder"] = not args.no_imap  # = yes_imap :D
        mail_data["plain_text"] = args.plain_text
        mail_info = mail_data_to_mail_info(mail_data)
        if args.test_mail:
            test_mail_sending(mail_info)
            exit(0)

        send_mails(gifter_giftee_tuple, mail_info)


if __name__ == "__main__":
    # Parsing des arguments
    args = parser.parse_args()

    try:
        data = safe_load(args.FICHIER)
    except scanner.ScannerError:
        logger.error("Impossible de charger le fichier d'entrée : yaml invalide.")
        exit(1)

    mail_data: dict[str, str] | None = None
    if args.auth:
        try:
            mail_data = safe_load(args.auth)
        except scanner.ScannerError:
            logger.error("Impossible de charger le fichier de configuration mail : yaml invalide.")
            exit(1)

        mail_data["message"] = args.message.read()
        mail_data["plain_text"] = args.plain_text

    # Exécution
    ronde_cadeaux(
        args,
        data=data,
        mail_data=mail_data,
    )
