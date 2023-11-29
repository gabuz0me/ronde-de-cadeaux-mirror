from typing import Dict

class Person:
    def __init__(self, id: str, data: Dict):
        self._name = id
        self._data = data

    def __str__(self):
        return self._name

    @property
    def name(self):
        if 'display_name' in self._data:
            return self._data['display_name']
        return self._name
    
    @property
    def nickname(self):
        if 'nickname' in self._data:
            return self._data['nickname']
        return self.name
    
    @property
    def email(self):
        return self._data['email']
        

def build_cluster_dict(cluster_data: Dict) -> Dict:
    """Construit un dictionnaire avec le nom d'une clique et la
    liste des personnes qui en font partie
    """

    cluster_dict = {}

    # On prend tout d'abord les listes de personnes
    for cluster_name, data in cluster_data.items():
        if 'people' in data:
            cluster_dict[cluster_name] = set(data['people'])

    # Et ensuite les listes de listes
    for cluster_name, data in cluster_data.items():
        if 'subclusters' in data:
            cluster_dict[cluster_name] = {
                person
                for subcluster_name in data['subclusters']
                for person in cluster_dict[subcluster_name]
            }

    return cluster_dict


def generate_graph(data: Dict) -> Dict:
    """Crée un dictionnaire dont les clés sont les participant⋅e⋅s de la ronde
    et les valeurs des listes de personnes pouvant être tirées par læ participant⋅e.
    """

    people = data['people']
    clusters = build_cluster_dict(data['clusters']) \
        if 'clusters' in data \
        else None

    # Initialisation du graphe
    graph = {
        gifter_id: set()
        for gifter_id, _ in people.items()
    }

    # Construction du graphe
    for gifter_id, gifter_data in people.items():
        had_allowlist = False

        # allowlist
        if 'allowlist' in gifter_data:
            had_allowlist = True
            graph[gifter_id] = set(gifter_data['allowlist'])

        # allowlist de clusters
        if clusters and 'allowlist_clusters' in gifter_data:
            had_allowlist = True
            graph[gifter_id] = \
                graph[gifter_id].union(
                    {
                        person
                        for cluster_name in gifter_data['allowlist_clusters']
                        for person in clusters[cluster_name]
                    }
            )

        # Si aucun des deux on considère que la personne peut
        # offrir à tout le monde
        if not had_allowlist:
            graph[gifter_id] = set([other_id for other_id in people.keys()])

        # denylist
        if 'denylist' in gifter_data:
            graph[gifter_id] = \
                graph[gifter_id].difference(
                    set(gifter_data['denylist'])
            )

        # denylist de clusters
        if clusters and 'denylist_clusters' in gifter_data:
            graph[gifter_id] = \
                graph[gifter_id].difference(
                    {
                        person
                        for cluster_name in gifter_data['denylist_clusters']
                        for person in clusters[cluster_name]
                    }
            )

        # On ne peut pas se piocher soi-même, mieux vaut s'en assurer
        graph[gifter_id].discard(gifter_id)

        # Enfin on transform le Set en List
        graph[gifter_id] = list(graph[gifter_id])

    return graph