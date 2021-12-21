from typing import Dict


def build_cluster_dict(cluster_data: Dict) -> Dict:
    """Construit un dictionnaire avec le nom d'une clique et la
    liste des personnes qui en font partie
    """

    cluster_dict = {}

    # On prend tout d'abord les listes de personnes
    for cluster in cluster_data:
        if 'people' in cluster:
            cluster_dict[cluster['name']] = set(cluster['people'])

    # Et ensuite les listes de listes
    for cluster in cluster_data:
        if 'subclusters' in cluster:
            cluster_dict[cluster['name']] = {
                person
                for subcluster_name in cluster['subclusters']
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
        gifter['name']: set()
        for gifter in people
    }

    # Construction du graphe
    for gifter in people:
        had_whitelist = False

        # Whitelist
        if 'whitelist' in gifter:
            had_whitelist = True
            graph[gifter['name']] = set(gifter['whitelist'])

        # Whitelist de clusters
        if clusters and 'whitelist_clusters' in gifter:
            had_whitelist = True
            graph[gifter['name']] = \
                graph[gifter['name']].union(
                    {
                        person
                        for cluster_name in gifter['whitelist_clusters']
                        for person in clusters[cluster_name]
                    }
            )

        # Si aucun des deux on considère que la personne peut
        # offrir à tout le monde
        if not had_whitelist:
            graph[gifter['name']] = set([person['name'] for person in people])

        # Blacklist
        if 'blacklist' in gifter:
            graph[gifter['name']] = \
                graph[gifter['name']].difference(
                    set(gifter['blacklist'])
            )

        # Blacklist de clusters
        if clusters and 'blacklist_clusters' in gifter:
            graph[gifter['name']] = \
                graph[gifter['name']].difference(
                    {
                        person
                        for cluster_name in gifter['blacklist_clusters']
                        for person in clusters[cluster_name]
                    }
            )

        # On ne peut pas se piocher soi-même, mieux vaut s'en assurer
        graph[gifter["name"]].discard(gifter["name"])

    return graph
