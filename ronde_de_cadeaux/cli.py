"""Point d'entrée de la CLI utilisée par `ronde`."""

import datetime
import random
import sys

from .graph_generation import GraphGenerationException, generate_people_graph, get_people_cycle
from .logger import logger
from .mail import send_mails, test_mail_sending
from .parser import ParserArgs
from .tools import compute_hamiltonian_cycle


def main() -> None:
    """C'est parti."""
    try:
        args = ParserArgs()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    if args.mail and args.mail.testing:
        test_mail_sending(args.mail)
        sys.exit(0)

    if args.seed:
        random.seed(args.seed)

    try:
        people_graph = generate_people_graph(args.people_and_groups)
    except GraphGenerationException as e:
        logger.error(f"Erreur dans la génération du graphe : {e.message}.")
        sys.exit(1)

    path = compute_hamiltonian_cycle(people_graph)
    if not path:
        logger.error("Pas de circuits trouvés, essayez d'amoindrir les contraintes.")
        sys.exit(1)

    draw = get_people_cycle(args.people_and_groups, path)

    if args.mail:
        send_mails(draw, args.mail)

    if args.show or args.output:
        max_name_length = max(len(p.name) for p, _ in draw)  # Aligner sur le nom le plus long
        text = "\n".join([f"{gifter.name:>{max_name_length}} → {giftee.name}" for gifter, giftee in draw])

        if args.show:
            logger.output(text)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(f"Tirage du {datetime.datetime.now().replace(microsecond=0)} :\n")
                f.write(text)
                f.write("\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
