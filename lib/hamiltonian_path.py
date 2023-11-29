from random import sample
from typing import Dict, List


def shuffled(sucessors: List) -> List:
    """Renvoie une liste mélangée créée à partir d'un set"""
    return sample(sucessors, len(sucessors))


def hamilton(graph: Dict, current_node: str, path: List = []) -> List:
    """Algorithme récursif permettant de trouver un cycle hamiltonien dans un graphe donné"""

    # print(f"{'   '*len(path)}→{current_node} [{len(path)}/{len(graph)}]")
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
            candidate_path = hamilton(graph, next_node, path)
            if candidate_path:
                return candidate_path

        path.pop()

    # Si nœud déjà dans chemin ou si pas trouvé de chemin possibles
    return None

def path_as_tuples(path: List) -> List:
    """Crée une liste de tuple `(gifter, giftee)` correspondant au `path` donné"""
    result = []
    N = len(path)
    for i in range(N):
        result.append( (path[i], path[(i+1)%N]) )
    return result