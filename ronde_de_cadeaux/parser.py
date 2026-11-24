"""Module de création du parser."""

import argparse
import sys
from pathlib import Path
from sys import argv
from textwrap import dedent
from typing import Any

from ._metadata import __homepage__, __version__
from .email import EmailInfo, create_email_info
from .i18n import _
from .logger import VerboseQuiet, logger, set_logger_level
from .people_graph_generation import create_people_and_groups_info
from .tools import ErrorCode


def _makeParser() -> argparse.ArgumentParser:
    """Fabrique et retourne le parser des arguments."""
    _SEE_SCHEMA = _("voir la documentation pour le schéma")

    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30),  # Décale le texte vers la droite
        prog="ronde",
        description=dedent(
            _("""\
            Ce programme permet de générer un tirage de gens à qui offrir
            des cadeaux en prenant en compte un système de contraintes
            complexes.
            """),
        ),
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help=_("affiche le numéro de version et termine le programme"),
    )

    verbose_quiet = parser.add_mutually_exclusive_group()
    verbose_quiet.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=_("active le mode verbeux"),
    )

    verbose_quiet.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help=_("réduit les messages affichés"),
    )

    parser.add_argument(
        "--test-email",
        action="store_true",
        help=_("teste la configuration du serveur de messagerie"),
    )

    parser.add_argument(
        "-a",
        "--auth",
        type=Path,
        help=_("fichier de configuration du serveur de messagerie pour l'envoi des courriels, %(see_schema)s")
        % {"see_schema": _SEE_SCHEMA},
    )

    parser.add_argument(
        "-m",
        "--message",
        type=Path,
        help=_("fichier patron du message envoyé par courriel, %(see_schema)s") % {"see_schema": _SEE_SCHEMA},
    )

    parser.add_argument(
        "-p",
        "--people",
        type=Path,
        help=_("fichier de configuration des personnes (YAML ou CSV, %(see_schema)s)") % {"see_schema": _SEE_SCHEMA},
    )

    parser.add_argument(
        "-s",
        "--show",
        help=_("affiche la ronde calculée"),
        action="store_true",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=_("fichier dans lequel exporter le tirage"),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=_("force l'écriture dans le fichier de sortie, même si celui-ci existe déjà"),
    )

    parser.add_argument(
        "--seed",
        help=_("graine aléatoire pour le tirage"),
    )

    return parser


class ParserArgs:
    """Structure représentant les données d'entrées après validation.

    Lève une `ValueError` s'il y a un problème.

    ---

    Represent the parser namespace after data validation.

    Raise `ValueError` if anything is wrong.
    """

    class NormalExit(Exception):
        """Le programme doit s'arrêter, sans que cela ne soit véritablement une erreur qui implique cet arrêt."""

        def __init__(self, code: ErrorCode, *args: object) -> None:
            self.code = code
            super().__init__(*args)

    def __init__(self, *, custom_args: str | list[str] | None = None) -> None:
        parser = _makeParser()
        if isinstance(custom_args, str):
            custom_args = custom_args.split()

        try:
            args = parser.parse_args(custom_args)  # arguments DIY pour les tests unitaires
        except SystemExit as e:
            logger.debug("argparse SystemExit")  # argparse lève un SystemExit pour `--help` (code 0)
            raise self.NormalExit(ErrorCode.OK if e.code == 0 else ErrorCode.ERROR_ARGPARSE) from None

        set_logger_level(VerboseQuiet(args.verbose, args.quiet))

        if len(argv) == 1:
            parser.print_help(sys.stderr)
            raise self.NormalExit(ErrorCode.ERROR_ARGPARSE)

        if args.version:
            print(__version__)
            raise self.NormalExit(ErrorCode.OK)

        self.email: EmailInfo | None = None
        self.show: bool = args.show
        self.output: Path | None = args.output
        self.seed: Any | None = args.seed

        if args.test_email:
            if not args.auth:
                raise ValueError(_("Fichier de configuration du serveur de messagerie manquant pour le test de connexion"))
            if args.people:
                create_people_and_groups_info(args.people, check_email_address=True)

        # Tirage
        else:
            if not (args.output or args.show or args.auth):
                raise ValueError(
                    _("""\
                    Effectuez au moins une action parmi afficher, écrire dans un fichier ou
                    envoyer par courriel le résultat du tirage
                    """)
                )

            if args.auth and not args.message:
                raise ValueError(_("Fichier de message manquant pour l'envoi des courriels"))
            if not args.auth and args.message:
                logger.warning(
                    _("Un fichier de message a été fourni, c'est inutile car aucune action relative aux courriels ne sera effectuée")
                )

            if not args.people:
                raise ValueError(_("Fichier décrivant les personnes manquant"))

            if self.output and self.output.exists() and not args.force:
                raise ValueError(_("Fichier de sortie déjà existant, utilisez '--force' pour l'écraser"))

            try:
                self.people_and_groups = create_people_and_groups_info(args.people, check_email_address=args.auth)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e) from e

        if args.auth:
            try:
                self.email = create_email_info(args.auth, args.message, args.test_email)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e) from e
