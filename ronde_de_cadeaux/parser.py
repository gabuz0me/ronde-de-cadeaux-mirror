"""Module de création du parser."""

import sys
from pathlib import Path
from sys import argv
from textwrap import dedent
from typing import Any

from . import __version__
from .email import EmailInfo, create_email_info
from .logger import logger
from .parser_translation import convert_argparse_to_french
from .people_graph_generation import create_people_and_groups_info

convert_argparse_to_french()  # À appeler avant l'import de argparse
import argparse  # noqa


def _makeParser() -> argparse.ArgumentParser:
    """Fabrique et retourne le parser des arguments."""
    parser = argparse.ArgumentParser(
        prog="ronde",
        description=dedent("""\
            Ce programme permet de générer un tirage de gens à qui offrir
            des cadeaux en prenant en compte un système de contraintes
            complexes.
            """),
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Afficher le numéro de version du programme et quitter",
    )

    parser.add_argument(
        "--test-email",
        action="store_true",
        help="Tester la configuration de l'envoi des courriels",
    )

    parser.add_argument(
        "-a",
        "--auth",
        type=Path,
        help="Fichier de configuration de l'envoi des courriels, voir la documentation pour le schéma",
    )

    parser.add_argument(
        "-m",
        "--message",
        type=Path,
        help="Fichier patron du message envoyé par courriel, voir la documentation pour le schéma",
    )

    parser.add_argument(
        "-p",
        "--people",
        type=Path,
        help="Fichier des personnes (YAML ou CSV, voir la documentation pour le schéma)",
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
        help="Forcer l'écriture dans le fichier de sortie, même si celui-ci existe déjà",
    )

    parser.add_argument(
        "--seed",
        help="Graine aléatoire pour le tirage",
    )

    return parser


class ParserArgs:
    """Structure représentant les données d'entrées après validation.

    Lève une `ValueError` s'il y a un problème.

    ---

    Represent the parser namespace after data validation.

    Raise `ValueError` if anything is wrong.
    """

    def __init__(self, *, custom_args: str | list[str] | None = None) -> None:
        parser = _makeParser()
        if isinstance(custom_args, str):
            custom_args = custom_args.split()
        args = parser.parse_args(custom_args)  # arguments DIY pour les tests unitaires

        if len(argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        if args.version:
            logger.info(__version__)
            sys.exit(0)

        self.email: EmailInfo | None = None
        self.show: bool = args.show
        self.output: Path | None = args.output
        self.seed: Any | None = args.seed

        if args.test_email:
            if not args.auth:
                raise ValueError("Fichier de configuration du serveur de messagerie manquant pour le test de connexion")
                # raise ValueError("Missing auth file for testing email configuration")
            if args.people:
                create_people_and_groups_info(args.people, check_email_address=True)

        # Tirage
        else:
            # Au moins une action
            if not (args.output or args.show or args.auth):
                raise ValueError("""\
                    Effectuez au moins une action parmi afficher, écrire dans un fichier ou
                    envoyer par courriel le résultat du tirage
                    """)
                # raise ValueError("Please show, write to a file or send by email the draw")
            # Courriel --> Message
            if args.auth and not args.message:
                raise ValueError("Fichier de message manquant pour l'envoi des courriels")
                # raise ValueError("Missing message file for email sending")
            if not args.auth and args.message:
                logger.warning(
                    "Un fichier de message a été fourni, c'est inutile car aucune action relative aux courriels ne sera effectuée"
                )
            if not args.people:
                raise ValueError("Fichier décrivant les personnes manquant")
                # raise ValueError("Missing input file for the draw")
            if self.output and self.output.exists() and not args.force:
                raise ValueError("Fichier de sortie déjà existant, utilisez `--force` pour l'écraser")
                # raise ValueError("Output file already exist, use `--force` to override")

            try:
                self.people_and_groups = create_people_and_groups_info(args.people, check_email_address=args.auth)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e)

        if args.auth:
            try:
                self.email = create_email_info(args.auth, args.message, args.test_email)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e)
