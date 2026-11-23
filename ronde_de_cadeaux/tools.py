"""Boîte à outils."""

import random
from enum import Enum, IntEnum, auto
from random import sample
from shutil import get_terminal_size
from textwrap import dedent, fill
from typing import TypeVar

import dns.resolver
import email_validator


class ErrorCode(IntEnum):
    """Code d'erreur standard."""

    OK = 0
    ERROR = 1
    ERROR_ARGPARSE = 2


class EmailValidator:
    """Valide les emails. Ou pas."""

    class ValidationStatus(Enum):
        """Statut de la validation."""

        OK = auto()
        UNKNOWN_DELIVERABILITY = auto()
        DNS_ERROR = auto()
        SYNTAX_ERROR = auto()

    def __init__(self) -> None:
        self._resolver = dns.resolver.Resolver(configure=False)
        self._resolver.nameservers = [
            "1.1.1.1",  # Cloudflare
            "8.8.8.8",  # Google
            "9.9.9.9",  # Quad9
        ]
        self._resolver.cache = dns.resolver.LRUCache()

    # https://www.emailawesome.com/blog/python-email-validation
    def validate(self, email: str) -> tuple[ValidationStatus, str]:
        """Valide ou pas une adresse courriel.

        Retour un tuple contenant le statut de la validation (`EmailValidator.ValidationStatus`) et l'adresse courriel normalisée.
        """  # noqa

        status = self.ValidationStatus.OK
        email_normalized = ""
        try:
            # valeur par défaut pour `check_deliverability` (None), ici vaut True en général, False pour les tests unitaires
            validated = email_validator.validate_email(
                email,
                check_deliverability=None,
                allow_smtputf8=False,
                dns_resolver=self._resolver,
            )
        except email_validator.EmailSyntaxError:
            status = self.ValidationStatus.SYNTAX_ERROR
        except email_validator.EmailUndeliverableError:
            status = self.ValidationStatus.DNS_ERROR
        else:
            email_normalized = validated.normalized
            if email_validator.CHECK_DELIVERABILITY and getattr(validated, "mx", None) is None:
                status = self.ValidationStatus.UNKNOWN_DELIVERABILITY
        return (status, email_normalized)


email_address_validator = EmailValidator()

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
    return "\n\n".join(
        [fill(dedent(paragraph), width=get_terminal_size().columns, break_on_hyphens=False) for paragraph in text.split("\n\n")]
    )
