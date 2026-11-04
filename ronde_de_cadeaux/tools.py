"""Boîte à outils."""

import random
from random import sample
from shutil import get_terminal_size
from textwrap import dedent, fill
from typing import TypeVar

import email_validator
from email_validator import ValidatedEmail
from email_validator import validate_email as _validate_email

from .logger import logger


# https://www.emailawesome.com/blog/python-email-validation
def validate_email(email: str) -> ValidatedEmail:
    """Wrapper de `email_validator.validate_email` avec les bons arguments."""  # noqa
    # valeur par défaut pour `check_deliverability` (None), ici vaut True en général, False pour les tests unitaires
    validated = _validate_email(
        email,
        check_deliverability=None,
        allow_smtputf8=False,
    )
    if email_validator.CHECK_DELIVERABILITY and getattr(validated, "mx", None) is None:
        logger.warning(f"La délivrabilité de {email} n'a pas pu être vérifiée. Peut-être que des erreurs auront lieu ¯\\_(ツ)_/¯")
    return validated


T = TypeVar("T")


def shuffled(successors: list[T]) -> list[T]:
    """Renvoie une liste mélangée créée à partir d'une liste."""
    return sample(successors, len(successors))


def list_as_cyclic_pairs(list_: list[T]) -> list[tuple[T, T]]:
    """Crée une liste cyclique de tuple `(A, B)` correspondant à une liste `list_` donnée.

    `[A, B, C]` -> `[(A,B), (B,C), (C,A)]`
    """
    result: list[tuple[T, T]] = []
    N = len(list_)
    for i in range(N):
        result.append((list_[i], list_[(i + 1) % N]))
    return result


Graph = dict[str, list[str]]


def compute_hamiltonian_cycle(graph: Graph, current_node: str | None = None, path: list[str] | None = None) -> list[str] | None:
    """Algorithme récursif permettant de trouver un cycle hamiltonien dans un graphe donné."""
    if current_node is None:
        current_node = random.choice(sorted(graph))  # sorted pour avoir un comportement déterministe

    if path is None:
        path = []

    if current_node not in path:
        path.append(current_node)

        # Si on a réussi à mettre tous les nœuds
        # C'est gagné si on a un cycle
        if len(path) == len(graph):
            if path[0] in graph[path[-1]]:
                return path
            else:
                path.pop()
                return None

        # Sinon, itération principale
        for next_node in shuffled(graph[current_node]):
            # copied_path = [i for i in path]
            candidate_path = compute_hamiltonian_cycle(graph, next_node, path)
            if candidate_path is not None:
                return candidate_path

        path.pop()

    # Si nœud déjà dans chemin ou si pas trouvé de chemin possibles
    return None


def fill_dedent(text: str) -> str:
    """Appelle `textwrap.dedent` sur le texte et `textwrap.fill` en ajustant à la taille du terminal."""
    return fill(dedent(text), width=get_terminal_size().columns)
