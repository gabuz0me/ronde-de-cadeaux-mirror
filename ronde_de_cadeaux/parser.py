"""Module de création du parser."""

import sys
from pathlib import Path
from sys import argv
from textwrap import dedent
from typing import Any

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
        "--text-format",
        choices=["html", "txt", "auto"],
        default="auto",
        help="Formatage du corps du mail (par défaut `auto`, essaye de détecter)",
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
        help="Forcer l'écriture dans le fichier de sortie, même si celui-ci existe déjà",
    )

    parser.add_argument(
        "--seed",
        help="Utilise cette graine aléatoire pour le tirage",
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

        self.mail: MailInfo | None = None
        self.show: bool = args.show
        self.output: Path | None = args.output
        self.seed: Any | None = args.seed

        if args.test_mail:
            if not args.auth:
                raise ValueError("Fichier de configuration mail manquant pour le test de connexion")
                # raise ValueError("Missing auth file for testing mail configuration")
        # Tirage
        else:
            # Au moins une action
            if not (args.output or args.show or args.auth):
                raise ValueError(
                    dedent(
                        """Effectuez au moins une action parmi afficher, écrire dans un fichier ou
                        envoyer par mail le résultat du tirage"""
                    )
                )
                # raise ValueError("Please show, write to a file or send by mail the draw")
            # Mail --> Message
            if args.auth and not args.message:
                raise ValueError("Fichier de message manquant pour l'envoi des mails")
                # raise ValueError("Missing message file for email sending")
            if not args.input:
                raise ValueError("Fichier d'entrée manquant")
                # raise ValueError("Missing input file for the draw")
            if self.output and self.output.exists() and not args.force:
                raise ValueError("Fichier de sortie déjà existant, utilisez `--force` pour l'écraser")
                # raise ValueError("Output file already exist, use `--force` to override")

            try:
                self.people_and_groups = create_people_and_groups_info(args.input, args.test_mail)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e)

        if args.auth:
            try:
                self.mail = create_mail_info(args.test_mail, args.auth, args.message, args.text_format.lower(), args.no_imap)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e)
