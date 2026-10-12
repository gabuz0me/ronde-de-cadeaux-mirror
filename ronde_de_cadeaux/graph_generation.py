"""Ici on s'occupe de générer les graphes de qui peut tirer qui."""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, NamedTuple, Protocol, override

import yaml
from pydantic import BaseModel, EmailStr, ValidationError

from .tools import Graph, list_as_cyclic_pairs


class _PersonModel(BaseModel):
    display_name: str | None = None
    nickname: str | None = None
    email: EmailStr | None = None  # Obligatoire pour envoyer des mails cependant. Vérifié dans `create_people_and_groups_info`
    allowlist: list[str] | None = None
    denylist: list[str] | None = None


class _PeopleModel(BaseModel):
    people: dict[str, _PersonModel | None]
    groups: dict[str, list[str]] | None = None


class PersonLike(Protocol):
    """Has the fields of a `Person`."""

    @property
    def id(self) -> str: ...  # noqa
    @property
    def name(self) -> str: ...  # noqa
    @property
    def nickname(self) -> str: ...  # noqa
    @property
    def email(self) -> str | None: ...  # noqa
    @property
    def allowlist(self) -> list[str]: ...  # noqa
    @property
    def denylist(self) -> list[str]: ...  # noqa


class PersonTuple(NamedTuple):  # noqa
    id: str
    name: str
    nickname: str
    email: str | None
    allowlist: list[str]
    denylist: list[str]


class Person:
    """Structure permettant de s'abstraire d'un dictionnaire."""

    def __init__(self, id_: str, data: _PersonModel | None) -> None:
        self.id = id_
        self._data = data or _PersonModel()  # On s'assure de construire un objet par défaut

    @override
    def __repr__(self) -> str:
        return f"Person:{self.id}"

    @property
    def name(self) -> str:
        """Renvoie le nom à afficher s'il existe, ou le nom classique à défaut."""
        return self._data.display_name or self.id

    @property
    def nickname(self) -> str:
        """Renvoie le surnom s'il existe, ou le nom à défaut."""
        return self._data.nickname or self.name

    @property
    def email(self) -> str | None:
        """Renvoie l'email de la personne."""
        return self._data.email

    @property
    def allowlist(self) -> list[str]:
        """Liste d'autorisation."""
        return self._data.allowlist or []

    @property
    def denylist(self) -> list[str]:
        """Liste de rejet."""
        return self._data.denylist or []


@dataclass
class PeopleAndGroups:
    """Classe principale décrivant les personnes impliquées dans ce joyeux petit moment.

    ---

    Main data class for the people involved in that happy little moment.
    """

    id_to_person: dict[str, Person]
    groups: dict[str, list[str]] | None = None

    @property
    def people(self):  # noqa
        return self.id_to_person.values()


def create_people_and_groups_info(people_path: Path, check_mail_address: bool = False) -> PeopleAndGroups:
    """Crée la structure des gens et des groupes en fonction du fichier d'entrée.

    Ne fait que valider les données d'un point de vue de la structure, rien n'ai fait quant au graphe.

    Délègue à `_create_people_and_groups_info`.

    Lève:
      - `ValueError` si le fichier est invalide.
      - `FileNotFoundError` si le fichier n'existe pas.

    ---

    Create the people and groups structure based on the path of the file.

    Only validates the data, no graph shenanigans are performed (yet).

    Delegates to `_create_people_and_groups_info`.

    Raise:
      - `ValueError` if invalid data is given.
      - `FileNotFoundError` if one of the files doesn't exist.
    """
    if not people_path.exists():
        raise FileNotFoundError(f"File {people_path} doesn't exist")
    with open(people_path, "r", encoding="utf-8") as f:
        try:
            people_data = yaml.safe_load(f)
        except yaml.YAMLError:
            raise ValueError("Fichier de donnée des gens invalide (YAML invalide)")
            # raise ValueError("Invalid people configuration file (Ill-formed YAML)")
    return _create_people_and_groups_info(people_data, check_mail_address)


def _create_people_and_groups_info(people_data: Any, check_mail_address: bool = False) -> PeopleAndGroups:  # noqa: ANN401
    """Version privée, utilisée pour les tests unitaires."""
    try:
        people = _PeopleModel.model_validate(people_data)
    except ValidationError:
        raise ValueError("Fichier de donnée des gens invalide (non conforme au schéma)")
        # raise ValueError("Invalid people configuration file (Invalid schema)")

    if check_mail_address:
        for person in people.people.values():
            if person is None or not person.email:
                raise ValueError(f"L'envoi de mail est activé mais la personne '{person}' n'a pas d'adresse mail")
                # raise ValueError(f"Mail sending is enabled, but person '{person}' has no email address")

    return PeopleAndGroups(
        {k: Person(k, v) for k, v in people.people.items()},
        people.groups,
    )


class GraphGenerationExceptionType(Enum):
    """Pour les tests unitaires.

    Permet de savoir à quel moment l'exception a été levée.
    """

    GENERIC = auto()
    INFINITE_RECURSION = auto()
    GROUP_IS_ALSO_PERSON = auto()
    UNDEFINED_CONSTRUCTING_CLUSTERS = auto()
    UNDEFINED_CONSTRUCTING_LISTS = auto()
    PEOPLE_EMPTY = auto()


class GraphGenerationException(Exception):
    """Classe d'exception relative aux graphes générés."""

    def __init__(
        self,
        message: str,
        type: GraphGenerationExceptionType = GraphGenerationExceptionType.GENERIC,
    ) -> None:
        super().__init__()
        self.message = message
        self.type = type


def _recursive_build_group_to_person_set_dict(
    group_data: dict[str, list[str]],  # group name to group/person list
    people_set: set[str],  # For easy lookup
    final_group_dict: dict[str, set[str]],  # group name to a list of people
    current_group_key: str,
    parent_groups_names: set[str] | None = None,
) -> None:
    """Fonction de construction des groupes.

    Au premier appel, construit l'ensemble des nœuds enfants de `current_group_key` dans `final_group_dict`.
    Pour ce faire on utilise les données contenues dans `group_data`. On tient la liste des groupes parents dans
    `parent_groups_names`. `people_set` sert à savoir si un élément est une clé pour le dict des gens ou des groupes.
    """
    if parent_groups_names is None:
        parent_groups_names = set()

    if current_group_key in final_group_dict:  # On est déjà passé par là
        return

    if current_group_key in parent_groups_names:
        raise GraphGenerationException(
            "Boucle infinie dans les groupes.",
            GraphGenerationExceptionType.INFINITE_RECURSION,
        )

    if current_group_key in people_set:
        raise GraphGenerationException(
            f"Le groupe '{current_group_key}' est aussi l'identifiant unique d'une personne.",
            GraphGenerationExceptionType.GROUP_IS_ALSO_PERSON,
        )

    parent_groups_names.add(current_group_key)
    data = group_data[current_group_key]  # data est une liste de ce qui est contenu dans un groupe

    # On trie d'un côté les gens et de l'autre les groupes
    set_people = set()
    set_groups = set()
    for element in data:
        if element in group_data:
            set_groups.add(element)
        elif element in people_set:
            set_people.add(element)
        else:
            raise GraphGenerationException(
                f"Le groupe ou la personne '{element}', présent·e dans le groupe '{current_group_key}' n'est pas défini·e.",
                GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_CLUSTERS,
            )

    # On itère récursivement sur les groupes
    for subgroup_name in set_groups:
        _recursive_build_group_to_person_set_dict(
            group_data,
            people_set,
            final_group_dict,
            subgroup_name,
            parent_groups_names,
        )
        set_people |= final_group_dict[subgroup_name]

    final_group_dict[current_group_key] = set_people
    parent_groups_names.remove(current_group_key)


def _build_group_to_person_set_dict(data: PeopleAndGroups, people_name_set: set[str]) -> dict[str, set[str]] | None:
    """Construit un dictionnaire avec le nom d'un groupe et la liste des personnes qui en font partie."""
    if data.groups is None:
        return None

    final_group_dict: dict[str, set[str]] = {}
    for group_name in data.groups.keys():
        _recursive_build_group_to_person_set_dict(data.groups, people_name_set, final_group_dict, group_name)
    return final_group_dict


def get_people_from_people_and_group_list(
    people_set: set[str],
    groups: dict[str, set[str]] | None,
    elements: list[str],  # personnes et groupes contenus dans la allow/deny list
    is_allowlist: bool,
    gifter_id: str,
) -> set[str]:
    """D'une liste composée de groupes et de personnes, on retourne toutes les
    personnes, qu'elles soient contenues initialement dans un groupe ou pas.
    """  # noqa
    final_set = set()
    for element in elements:
        if element in people_set:
            final_set.add(element)
        elif groups is not None and element in groups:
            for person in groups[element]:
                final_set.add(person)
        else:
            which_list = "liste d'autorisation" if is_allowlist else "liste de rejet"
            raise GraphGenerationException(
                f"Le groupe ou la personne '{element}'," + f"présent·e dans la {which_list} de {gifter_id} n'est pas défini·e.",
                GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_LISTS,
            )

    return final_set


def generate_people_graph(data: PeopleAndGroups) -> Graph:
    """Génère le graphe final.

    Crée un dictionnaire dont les clés sont les participant⋅e⋅s de la ronde
    et les valeurs des listes de personnes pouvant être tirées par læ participant⋅e.
    """
    if len(data.people) == 0:
        raise GraphGenerationException(
            "Il n'y a aucune personne à tirer.",
            GraphGenerationExceptionType.PEOPLE_EMPTY,
        )

    people_name_set = {p.id for p in data.people}  # Helps to know if a given str is a group or a person. Created once, used multiple time.
    groups = _build_group_to_person_set_dict(data, people_name_set)

    # Construction du graphe
    graph = {}
    for gifter in data.people:
        # On calcule toutes les personnes qu'on a le droit de tirer
        allowlist = people_name_set
        if gifter.allowlist:
            allowlist = get_people_from_people_and_group_list(people_name_set, groups, gifter.allowlist, True, gifter.id)

        # On calcule toutes les personnes qu'on n'a pas le droit de tirer
        denylist = set()
        if gifter.denylist:
            denylist = get_people_from_people_and_group_list(people_name_set, groups, gifter.denylist, False, gifter.id)

        # On soustrait les deux
        final_set = allowlist - denylist

        # On ne peut pas se piocher soi-même, mieux vaut s'en assurer
        final_set.discard(gifter.id)

        # Enfin on transform le Set en List et on le met dans le graphe final
        graph[gifter.id] = sorted(final_set)  # sorted pour avoir un comportement déterministe

    return graph


Draw = list[tuple[Person, Person]]


def get_people_cycle(people: PeopleAndGroups, path: list[str]) -> Draw:
    """D'un cycle donné (`path_`), retourne une liste de paire de `Person` (Offreureuse, Destinataire).

    ---

    From a given cycle (`path_`), return the draw as a list of pair or `Person` (Gifter, Giftee).
    """
    path_person = [people.id_to_person[id_] for id_ in path]
    return list_as_cyclic_pairs(path_person)
