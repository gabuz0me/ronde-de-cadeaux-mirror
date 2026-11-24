"""Module de création du parser."""

import argparse
import re
import sys
from pathlib import Path
from sys import argv
from typing import Any

from ._metadata import __homepage__, __version__
from .email import EmailInfo, create_email_info
from .i18n import _
from .logger import Color, Style, VerboseQuiet, as_link, colored, logger, set_logger_level
from .people_graph_generation import create_people_and_groups_info
from .tools import ErrorCode, fill_dedent


def _makeParser() -> argparse.ArgumentParser:
    """Fabrique et retourne le parser des arguments."""
    _SEE_SCHEMA = _("voir la documentation pour le schéma")

    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog,
            max_help_position=30,  # Décale le texte vers la droite
        ),
        prog="ronde",
        description=fill_dedent(
            _("""\
            Ce programme permet de générer un tirage de gens à qui offrir
            des cadeaux en prenant en compte un système de contraintes
            complexes.

            Ces tirages peuvent ensuite être affichés, exportés ou envoyés par courriel.
            """)
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
        help=_("envoie un courriel de test via l'adresse expéditrice pour vérifier la configuration du serveur de messagerie"),
    )

    parser.add_argument(
        "-e",
        "--email-config",
        type=Path,
        help=_("fichier de configuration du serveur de messagerie pour l'envoi des courriels, %(see_schema)s")
        % {"see_schema": _SEE_SCHEMA},
        metavar=_("FICHIER"),
    )

    parser.add_argument(
        "-m",
        "--message",
        type=Path,
        help=_("fichier de gabarit du message envoyé par courriel (HTML ou texte, voir la documentation pour le formatage)"),
        metavar=_("FICHIER"),
    )

    parser.add_argument(
        "-p",
        "--people",
        type=Path,
        help=_("fichier de configuration des personnes (YAML ou CSV, %(see_schema)s)") % {"see_schema": _SEE_SCHEMA},
        metavar=_("FICHIER"),
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
        metavar=_("FICHIER"),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=_("force l'écriture dans le fichier de sortie, même si celui-ci existe déjà"),
    )

    parser.add_argument(
        "--seed",
        help=_("graine aléatoire pour le tirage"),
        metavar=_("GRAINE"),
    )

    # On utilise `replace` pour que `fill_dedent` utilise la bonne largeur de texte
    # (ie (sans les éventuels `%(...)s` en plus ou les `{c("txt")}` d'une f-string) )
    # pour l'affichage. Et c'est moins relou dans la traduction dans les .po aussi.
    epilog = fill_dedent(
        _(
            """\
            L'option --email-config nécessite qu'un fichier de gabarit de
            message soit passé avec --message.

            Si l'option --test-email est passée, il faut également passer --email-config. Un fichier
            de gabarit de message peut être donné optionnellement avec --message pour s'assurer du rendu.

            Quand la connexion au serveur de messagerie n'est pas testée, il faut nécessairement
            passer un fichier de configuration des personnes avec --people ainsi qu'effectuer au
            moins une des trois actions possibles parmi afficher (--show), exporter dans un fichier
            (--output) ou envoyer le tirage par mail (--email-config).

            Pour plus d'information, voir la documentation.
            """
        )
    )

    long_pattern = r"(--[\w-]+)"  # tous les textes de la forme `--longue-option`
    for pattern in set(re.findall(long_pattern, epilog)):
        epilog = epilog.replace(pattern, colored(pattern, Color.CYAN, Style.BOLD))
    epilog = epilog.replace(
        _("voir la documentation"),
        as_link(__homepage__, colored(_("voir la documentation"), Color.BLUE, Style.ITALIC)),
    )
    parser.epilog = epilog

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
            if not args.email_config:
                raise ValueError(_("Fichier de configuration du serveur de messagerie manquant pour le test de connexion"))
            if args.people:
                create_people_and_groups_info(args.people, check_email_address=True)

        # Tirage
        else:
            if not (args.output or args.show or args.email_config):
                raise ValueError(
                    _("""\
                    Effectuer au moins une action parmi afficher, écrire dans un fichier ou
                    envoyer par courriel le résultat du tirage
                    """)
                )

            if args.email_config and not args.message:
                raise ValueError(_("Fichier de message manquant pour l'envoi des courriels"))
            if not args.email_config and args.message:
                logger.warning(
                    _("Un fichier de message a été fourni, c'est inutile car aucune action relative aux courriels ne sera effectuée")
                )

            if not args.people:
                raise ValueError(_("Fichier décrivant les personnes manquant"))

            if self.output and self.output.exists() and not args.overwrite:
                raise ValueError(_("Fichier de sortie déjà existant, utiliser '--overwrite' pour l'écraser"))

            try:
                self.people_and_groups = create_people_and_groups_info(args.people, check_email_address=args.email_config)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e) from e

        if args.email_config:
            try:
                self.email = create_email_info(args.email_config, args.message, args.test_email)
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(e) from e
