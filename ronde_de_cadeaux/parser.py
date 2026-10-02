"""Module de création du parser."""

import sys
from pathlib import Path
from sys import argv
from textwrap import dedent

from ronde_de_cadeaux.graph_generation import create_people_and_groups_info

from .mail import MailInfo, create_mail_info
from .parser_translation import convert_argparse_to_french

convert_argparse_to_french()  # À appeler avant l'import de argparse
import argparse  # noqa


def _makeParser() -> argparse.ArgumentParser:
    """Fabrique et retourne le parser des arguments."""
    parser = argparse.ArgumentParser(
        prog="ronde",
        description=dedent("""\
            Ce programme permet de générer un tirage de gens à qui offrir
            des cadeaux en prenant en compte un système de contraintes
            complexes. Si un chemin hamiltonien est trouvé, un mail est
            envoyé à chacun⋅e des participant⋅e⋅s leur indiquant à qui
            offrir un présent.
            """),
    )

    parser.add_argument(
        "-t",
        "--test-mail",
        action="store_true",
        help="Tester la configuration de mail (si --auth est fourni)",
    )

    parser.add_argument(
        "-a",
        "--auth",
        type=Path,
        help="Fichier de configuration mail",
    )

    parser.add_argument(
        "-m",
        "--message",
        type=Path,
        help="Fichier mail type",
    )

    parser.add_argument(
        "-n",
        "--no-imap",
        help="Ne pas copier les mails dans la boîte d'envoi",
        action="store_true",
    )

    parser.add_argument(
        "-p",
        "--plain-text",
        action="store_true",
        help="Envoyer un mail au format texte à la place de HTML",
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Fichier yaml des données d'entrer à parser",
    )

    parser.add_argument(
        "-s",
        "--show",
        help="Afficher la ronde calculée",
        action="store_true",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Fichier dans lequel exporter le tirage",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Forcer l'écriture dans le fichier de sortie, même si celui-ci existe déjà.",
    )

    return parser


class ParserArgs:
    """Represent the parser namespace after data validation.

    Raise `ValueError` if anything is wrong.
    """

    def __init__(self) -> None:
        parser = _makeParser()
        args = parser.parse_args()

        if len(argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        self.mail: MailInfo | None = None
        self.show: bool = args.show
        self.output: Path | None = args.output

        if args.test_mail:
            if not args.auth:
                raise ValueError("Missing auth file for testing mail configuration")
        # Drawing
        else:
            # At least one action
            if not (args.output or args.show or args.auth):
                raise ValueError("Please show, write to a file or send by mail the draw")
            # Mail --> Message
            if args.auth and not args.message:
                raise ValueError("Missing message file for email sending")
            # Provide an input file
            if not args.input:
                raise ValueError("Missing input file for the draw")
            # If we output to a file, it better not exist already # TODO Should we really test?
            if self.output and self.output.exists() and not args.force:
                raise ValueError("Output file already exist, use `--force` to override")

            self.people_and_groups = create_people_and_groups_info(args.test_mail, args.input)

        if args.auth:
            self.mail = create_mail_info(args.test_mail, args.auth, args.message, args.plain_text, args.no_imap)
