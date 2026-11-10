"""Point d'entrée de la CLI utilisée par `ronde`."""

import datetime
import random
import sys

import email_validator

from .logger import logger
from .mail import Mailer, send_emails, test_email_sending
from .parser import ParserArgs
from .people_graph_generation import GraphGenerationException, generate_people_graph, get_people_cycle
from .tools import compute_hamiltonian_cycle


def main() -> None:
    """C'est parti."""
    email_validator.CHECK_DELIVERABILITY = True

    try:
        logger.debug("Parsing args...", newline=False)
        args = ParserArgs()
        logger.debug("OK")
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    if args.email and args.email.testing:
        try:
            logger.debug("Testing email config")
            test_email_sending(args.email)
            logger.debug("OK")
        except Mailer.BaseError as e:
            logger.error(f"Erreur lors du test de l'envoi des courriels : {e}")
            sys.exit(1)
        else:
            logger.info("Test de l'envoi des courriels : Tout à l'air de fonctionner :D")
        sys.exit(0)

    if args.seed:
        random.seed(args.seed)

    try:
        logger.debug("Generating people graph...", newline=False)
        people_graph = generate_people_graph(args.people_and_groups)
        logger.debug("OK")
    except GraphGenerationException as e:
        logger.error(f"Erreur dans la génération du graphe : {e.message}.")
        sys.exit(1)

    logger.debug("Computing hamiltonian cycle...", newline=False)
    path = compute_hamiltonian_cycle(people_graph)
    logger.debug("OK")

    if not path:
        logger.error("Pas de circuits trouvés, essayez d'amoindrir les contraintes.")
        sys.exit(1)

    draw = get_people_cycle(args.people_and_groups, path)

    if args.show or args.output:
        max_name_length = max(len(p.name) for p, _ in draw)  # Aligner sur le nom le plus long
        text = "\n".join([f"{gifter.name:>{max_name_length}} → {giftee.name}" for gifter, giftee in draw])

        if args.show:
            logger.info(text, dedent=False)  # Affiche dans la console le tirage tel quel

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(f"Tirage du {datetime.datetime.now().replace(microsecond=0)} :\n")
                f.write(text)
                f.write("\n")

    if args.email:
        try:
            logger.debug("Sending emails...")
            send_emails(draw, args.email)
            logger.debug("Sending emails OK")

        except Mailer.BaseError as e:
            logger.error(f"Erreur lors de l'envoi des courriels aux participant·e·s : {e}")
            sys.exit(1)
        else:
            logger.info("Tirage bien envoyé par mail :D")


if __name__ == "__main__":
    main()
