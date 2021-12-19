from typing import Dict, List


def hamilton(graph: Dict, size: int, current_node: str, path: List = []) -> List:
    if current_node not in set(path):
        path.append(current_node)
        if len(path) == size: # si on a réussi à mettre tous les nœuds c'est gagné
            return path
        for next_node in graph.get(current_node, []):
            res_path = [i for i in path] # régénération d'un chemin
            candidate = hamilton(graph, size, next_node, res_path)
            if candidate is not None:
                return candidate

    else:
        return None
