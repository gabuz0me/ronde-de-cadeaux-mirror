from enum import Enum, auto
from typing import Dict, Set, List


class GraphGenerationExceptionType(Enum):
    """Pour les tests unitaires.
    Permet de savoir à quel moment l'exception a été levée.
    """
    GENERIC = auto()
    INFINITE_RECURSION = auto()
    CLUSTER_IS_ALSO_PERSON = auto()
    UNDEFINED_CONSTRUCTING_CLUSTERS = auto()
    UNDEFINED_CONSTRUCTING_LISTS = auto()
    PEOPLE_EMPTY = auto()


class GraphGenerationException(Exception):
    def __init__(self, message: str, type = GraphGenerationExceptionType.GENERIC):
        self.message = message
        self.type = type


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


def recursive_build_cluster(cluster_data: Dict, people_set : Set[str], final_cluster_dict: Dict, current_cluster_key: str, parent_clusters_names: Set[str] = set()) -> None:
    """Au premier appel, construit l'ensemble des nœuds enfants de `current_cluster_key` dans `final_cluster_dict`.
    Pour ce faire on utilise les données contenues dans `cluster_data`. On tient la liste des clusters parents dans
    `parent_clusters_names`. `people_set` sert à savoir si un élément est une clé pour le dict des gens ou des groupes.
    """

    if current_cluster_key in final_cluster_dict: # On est déjà passé par là
        return

    if current_cluster_key in parent_clusters_names:
        raise GraphGenerationException("Boucle infinie dans les groupes.", GraphGenerationExceptionType.INFINITE_RECURSION)
    
    if current_cluster_key in people_set:
        raise GraphGenerationException(f"Le cluster '{current_cluster_key}' est aussi l'identifiant unique d'une personne.", GraphGenerationExceptionType.CLUSTER_IS_ALSO_PERSON)

    parent_clusters_names.add(current_cluster_key)
    data = cluster_data[current_cluster_key] # data est une liste de ce qui est contenu dans un cluster

    # On trie d'un côté les gens et de l'autre les groupes
    set_people = set()
    set_clusters = set()
    for element in data:
        if element in cluster_data:
            set_clusters.add(element)
        elif element in people_set:
            set_people.add(element)
        else:
            raise GraphGenerationException(f"Le groupe ou la personne '{element}', présent·e dans le groupe '{current_cluster_key}' n'est pas défini·e.", GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_CLUSTERS)

    # On itère récursivement sur les groupes
    for subcluster_name in set_clusters:
        recursive_build_cluster(cluster_data, people_set, final_cluster_dict, subcluster_name, parent_clusters_names)
        set_people |= final_cluster_dict[subcluster_name]

    final_cluster_dict[current_cluster_key] = set_people
    parent_clusters_names.remove(current_cluster_key)


def build_cluster_dict(cluster_data: Dict | None, people_set: Set[str]) -> Dict:
    """Construit un dictionnaire avec le nom d'un groupe et la
    liste des personnes qui en font partie.
    """

    if cluster_data is None:
        return None
    
    cluster_dict = {}
    for cluster_name in cluster_data.keys():
        recursive_build_cluster(cluster_data, people_set, cluster_dict, cluster_name)
    return cluster_dict

def get_people_from_people_and_cluster_list(people_set: Set[str], clusters: Dict, elements: List[str], is_allowlist: bool, gifter_id: str) -> Set[str]:
    """D'une liste composée de groupes et de personnes, on retourne toutes les personnes, qu'elles
    soient contenues initalement dans un groupe ou pas
    """
    final_set = set()
    for element in elements:
        if element in people_set:
            final_set.add(element)
        elif clusters is not None and element in clusters:
            for person in clusters[element]:
                final_set.add(person)
        else:
            which_list = 'allowlist' if is_allowlist else 'denylist'
            raise GraphGenerationException(f"Le groupe ou la personne '{element}', présent·e dans la '{which_list}' de '{gifter_id}' n'est pas défini·e.", GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_LISTS)

    return final_set


def generate_graph(data: Dict) -> Dict:
    """Crée un dictionnaire dont les clés sont les participant⋅e⋅s de la ronde
    et les valeurs des listes de personnes pouvant être tirées par læ participant⋅e.
    """

    people = data.get('people')
    if people is None or len(people) == 0 :
        raise GraphGenerationException(f"Il n'y a aucune personne à tirer.", GraphGenerationExceptionType.PEOPLE_EMPTY)
    people_set = {p for p in people.keys()}

    clusters = build_cluster_dict(data.get('clusters'), people_set)

    # Construction du graphe
    graph = {}
    for gifter_id, gifter_data in people.items():

        # On calcule toutes les personnes qu'on a le droit de tirer
        allowlist = set()
        if 'allowlist' in gifter_data:
            allowlist = get_people_from_people_and_cluster_list(people_set, clusters, gifter_data['allowlist'], True, gifter_id)
        else:
            allowlist = people_set

        # On calcule toutes les personnes qu'on n'a pas le droit de tirer
        denylist = set()
        if 'denylist' in gifter_data:
            denylist = get_people_from_people_and_cluster_list(people_set, clusters, gifter_data['denylist'], False, gifter_id)

        # On soustrait les deux
        final_set = allowlist - denylist
        
        # On ne peut pas se piocher soi-même, mieux vaut s'en assurer
        final_set.discard(gifter_id)

        # Enfin on transform le Set en List et on le met dans le graphe final
        graph[gifter_id] = list(final_set)

    return graph
