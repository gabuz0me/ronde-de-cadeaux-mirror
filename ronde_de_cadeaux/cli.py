"""Point d'entrée de la CLI utilisée par `ronde`."""

import datetime
import random
import sys

import email_validator

from .email import Emailer, send_emails, test_email_sending
from .logger import logger
from .parser import ParserArgs
from .people_graph_generation import GraphGenerationException, generate_people_graph, get_people_cycle
from .tools import ErrorCode, compute_hamiltonian_cycle


def main() -> ErrorCode:
    """C'est parti."""
    email_validator.CHECK_DELIVERABILITY = True

    try:
        args = ParserArgs()
    except ParserArgs.NormalExit as e:
        return e.code
    except Exception as e:
        logger.error(str(e))
        return ErrorCode.ERROR_ARGPARSE

    if args.email and args.email.testing:
        try:
            logger.debug("Test de la configuration des courriels...")
            test_email_sending(args.email)
        except Emailer.BaseError as e:
            logger.error(f"Erreur lors du test de l'envoi des courriels : {e}")
            return ErrorCode.ERROR
        else:
            logger.info("Test de l'envoi des courriels : Tout à l'air de fonctionner :D")
        return ErrorCode.OK

    if args.seed:
        random.seed(args.seed)

    try:
        logger.debug("Génération du graphe des gens...")
        people_graph = generate_people_graph(args.people_and_groups)
    except GraphGenerationException as e:
        logger.error(f"Erreur dans la génération du graphe : {e.message}.")
        return ErrorCode.ERROR

    logger.debug("Calcul d'un cycle hamiltonien..")
    path = compute_hamiltonian_cycle(people_graph)

    if not path:
        logger.error("Pas de circuits trouvés, essayez d'amoindrir les contraintes.")
        return ErrorCode.ERROR

    draw = get_people_cycle(args.people_and_groups, path)

    if args.show or args.output:
        max_name_length = max(len(p.name) for p, _ in draw)  # Aligner sur le nom le plus long
        text = "\n".join([f"{gifter.name:>{max_name_length}} → {giftee.name}" for gifter, giftee in draw])

        if args.show:
            print(text)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(f"Tirage du {datetime.datetime.now().replace(microsecond=0)} :\n")
                f.write(text)
                f.write("\n")

    if args.email:
        try:
            logger.debug("Envoi des courriels...")
            send_emails(draw, args.email)
            logger.debug("Envoi des courriels OK")

        except Emailer.BaseError as e:
            logger.error(f"Erreur lors de l'envoi des courriels aux participant·e·s : {e}")
            return ErrorCode.ERROR
        else:
            logger.info("Tirage bien envoyé par courriel \\o/")

    return ErrorCode.OK


if __name__ == "__main__":
    sys.exit(main())
