"""Point d'entrée de la CLI utilisée par `ronde`."""

import datetime
import random
import sys

import email_validator

from .email import Emailer, send_emails, test_email_sending
from .i18n import _, find_user_language, set_app_language
from .logger import logger, set_logger_level
from .parser import ParserArgs
from .people_graph_generation import GraphGenerationException, generate_people_graph, get_people_cycle
from .tools import ErrorCode, compute_hamiltonian_cycle


def main(argv: list[str] | None = None) -> ErrorCode:
    """Point d'entrée de `ronde-de-cadeaux`."""
    email_validator.CHECK_DELIVERABILITY = True
    set_logger_level()  # Initialise le niveau du logger avec DEBUG si la variable `RONDE_DEBUG` vaut 1
    set_app_language(find_user_language())

    try:
        args = ParserArgs(custom_args=argv)
    except ParserArgs.NormalExit as e:
        return e.code
    except Exception as e:
        logger.error(str(e))
        return ErrorCode.ERROR_ARGPARSE

    if args.email and args.email.testing:
        try:
            logger.debug(_("Test de la configuration des courriels..."))
            test_email_sending(args.email)
        except Emailer.BaseError as e:
            logger.error(_("Erreur lors du test de l'envoi des courriels : %(error)s") % {"error": e})
            return ErrorCode.ERROR
        else:
            logger.info(_("Test de l'envoi des courriels : Tout à l'air de fonctionner :D"))
        return ErrorCode.OK

    if args.seed:
        random.seed(args.seed)

    try:
        logger.debug(_("Génération du graphe des gens..."))
        people_graph = generate_people_graph(args.people_and_groups)
    except GraphGenerationException as e:
        logger.error(_("Erreur dans la génération du graphe : %(error)s") % {"error": e.message})
        return ErrorCode.ERROR

    logger.debug(_("Calcul d'un cycle hamiltonien..."))
    path = compute_hamiltonian_cycle(people_graph)

    if not path:
        logger.error(_("Pas de circuits trouvés, essayez d'amoindrir les contraintes"))
        return ErrorCode.ERROR

    draw = get_people_cycle(args.people_and_groups, path)

    if args.show or args.output:
        max_name_length = max(len(p.name) for p, _ in draw)  # Aligner sur le nom le plus long
        text = "\n".join([f"{gifter.name:>{max_name_length}} → {giftee.name}" for gifter, giftee in draw])

        if args.show:
            print(text)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(_("Tirage du %(datetime)s :") % {"datetime": datetime.datetime.now().replace(microsecond=0)})
                f.write("\n")
                f.write(text)
                f.write("\n")

    if args.email:
        try:
            logger.debug(_("Envoi des courriels..."))
            send_emails(draw, args.email)
            logger.debug(_("Envoi des courriels OK"))

        except Emailer.BaseError as e:
            logger.error(_("Erreur lors de l'envoi des courriels aux participant·e·s : %(error)s") % {"error": e})
            return ErrorCode.ERROR
        else:
            logger.info(_("Tirage bien envoyé par courriel \\o/"))

    return ErrorCode.OK


if __name__ == "__main__":
    sys.exit(main())
