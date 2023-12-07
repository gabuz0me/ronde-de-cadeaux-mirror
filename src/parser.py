import pathlib
from textwrap import dedent
from . import parser_translation

parser_translation.convert_argparse_to_french() # À appeler avant l'import de argparse
import argparse


DEFAULT_MAIL_TEMPLATE = (pathlib.Path(__file__).parent / '../message.txt').resolve()

def makeParser() -> argparse.ArgumentParser:
    """Fabrique et retourne le parser des arguments"""
    parser = argparse.ArgumentParser(
        description=dedent("""\
            Ce programme permet de générer un tirage de gens à qui offrir
            des cadeaux en prenant en compte un système de contraintes
            complexes. Si un chemin hamiltonien est trouvé, un mail est
            envoyé à chacun⋅e des participant⋅e⋅s leur indiquant à qui
            offrir un présent.
            """
        ),
    )

    parser.add_argument(
        'FICHIER',
        type=argparse.FileType('r', encoding='utf-8'),
        help="Fichier yaml des données d'entrer à parser",
    )

    parser.add_argument(
        '-s', '--show',
        help="Afficher la ronde calculée",
        action='store_true',
    )

    parser.add_argument(
        '-a', '--auth',
        type=argparse.FileType('r', encoding='utf-8'),
        help="Fichier de configuration mail",
    )

    parser.add_argument(
        '-n', '--no-imap',
        help="Ne pas copier les mails dans la boîte d'envoi",
        action='store_true',
    )

    parser.add_argument(
        '-m', '--message',
        type=argparse.FileType('r', encoding='utf-8'),
        help="Fichier mail type (Par défaut : %(default)s)",
        default=str(DEFAULT_MAIL_TEMPLATE),
    )

    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('a', encoding='utf-8'),
        help="Fichier dans lequel exporter le tirage",
    )

    return parser


parser = makeParser()
