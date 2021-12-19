from typing import Dict


def build_cluster_dict(cluster_data: Dict) -> Dict:
    # fonction qui construit un dictionnaire avec le nom d'une clique et la
    # lste des personnes qui en font partie
    cluster_dict = {cluster["name"]: set() for cluster in cluster_data} # initialisation

    for cluster in cluster_data:
        if "people" in cluster: # on prend tout d'abord les listes de personnes
            cluster_dict[cluster["name"]] = cluster_dict[cluster["name"]].union(set(cluster["people"]))

    for cluster in cluster_data:
        if "subclusters" in cluster: # et ensuite les listes de listes
            for subcluster in cluster["subclusters"]:
                cluster_dict[cluster["name"]] = cluster_dict[cluster["name"]].union(set(cluster_dict[subcluster]))

    return cluster_dict


def graph_gen(data: Dict) -> Dict:
    people = data["people"]

    # fonction qui génère le dictionnaire qui associe à chaque personne les
    # gens qu'elle a le droit de tirer
    graph = {gifter["name"]: set() for gifter in people}

    if "clusters" in data:
        # si des clusters sont définis, les whitelist et blacklist sont des
        # noms de groupes de personnes
        clusters = build_cluster_dict(data["clusters"])

        for gifter in people:
            if "whitelist" in gifter:
                for group in gifter["whitelist"]:
                    graph[gifter["name"]] = graph[gifter["name"]].union(clusters[group])
            else:
                # si la whitelist n'est pas définie, par défaut on peut piocher
                # tout le monde
                graph[gifter["name"]] = {receiver["name"] for receiver in people}

            if "blacklist" in gifter:
                # on enlève les gens blacklistés
                for group in gifter["blacklist"]:
                    graph[gifter["name"]] = graph[gifter["name"]].difference(clusters[group])

    else:
        # sinon, ce sont des listes de personnes
        for gifter in people:
            if "whitelist" in gifter:
                graph[gifter["name"]] = set(gifter["whitelist"])
            else:
                graph[gifter["name"]] = {receiver["name"] for receiver in people}

            if "blacklist" in gifter:
                graph[gifter["name"]] = graph[gifter["name"]].difference(set(gifter["blacklist"]))

    for gifter in people:
        # on ne peut pas se piocher soi-même, mieux vaut s'en assurer
        graph[gifter["name"]].discard(gifter["name"])

    return graph
