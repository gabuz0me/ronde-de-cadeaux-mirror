"""Partie algo de la génération de graphe."""

import random
from random import sample
from typing import TypeVar

T = TypeVar("T")


def shuffled(successors: list[T]) -> list[T]:
    """Renvoie une liste mélangée créée à partir d'un set."""
    return sample(successors, len(successors))


def path_as_tuples(path: list[T]) -> list[tuple[T, T]]:
    """Crée une liste de tuple `(gifter, giftee)` correspondant au `path` donné."""
    result: list[tuple[T, T]] = []
    N = len(path)
    for i in range(N):
        result.append((path[i], path[(i + 1) % N]))
    return result


Graph = dict[str, list[str]]


def compute_hamiltonian_cycle(graph: Graph, current_node: str | None = None, path: list[str] | None = None) -> list[str] | None:
    """Algorithme récursif permettant de trouver un cycle hamiltonien dans un graphe donné."""
    if current_node is None:
        current_node = random.choice(list(graph))

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
