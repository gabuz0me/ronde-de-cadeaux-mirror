import random
from typing import Any

import yaml

from ronde_de_cadeaux.graph_generation import (
    GraphGenerationException,
    GraphGenerationExceptionType,
    _create_people_and_groups_info,
    generate_people_graph,
)
from ronde_de_cadeaux.tools import compute_hamiltonian_cycle
from tests.base import RondeTest

DataAndBool = tuple[dict[str, Any], bool]  # Données des gens associées à un booléen "envoyer les mails ?"


PEOPLE_MINIMAL = """\
people:
    Alice:
"""

PEOPLE_MAXIMAL = """\
people:
    Alice:
        display_name: "Alice Ecila"
        nickname: "Al"
        email: "alice@eci.la"
        allowlist:
            - Bob
            - Alice
        denylist:
            - Eve
            - Bob
    Bob:
        display_name: "Robert Trebor"
        nickname: "Bobby"
        email: "robert@treb.or"
        allowlist:
            - Eve
        denylist:
            - Alice
    Eve:
        display_name: "Evelyn Nyleve"
        nickname: "Evelyn"
        email: "evelyn@nyle.ve"
        allowlist:
            - Alice
        denylist:
            - Bob
"""


class PeopleValidationTest(RondeTest):
    def test_invalid_data(self):
        data_list: list[DataAndBool] = []
        data_list.append(({}, False))  # Vide et incorrect, il manque "people"
        data_list.append((yaml.safe_load(PEOPLE_MINIMAL), True))

        for data in data_list:
            with self.assertRaises(ValueError):
                _create_people_and_groups_info(*data)

    def test_valid_data(self):
        data_list: list[DataAndBool] = []

        # Vide mais correct quant au schéma car contient la clé "people".
        # Ce cas est détecté lors de la génération du graphe.
        data_list.append(({"people": {}}, False))
        data_list.append((yaml.safe_load(PEOPLE_MINIMAL), False))
        data_list.append((yaml.safe_load(PEOPLE_MAXIMAL), True))

        for data in data_list:
            try:
                _create_people_and_groups_info(*data)
            except Exception as e:  # noqa: BLE001
                self.fail(e)

    def test_valid_fields_minimal(self):
        data = yaml.safe_load(PEOPLE_MINIMAL)
        people = _create_people_and_groups_info(data)
        alice = people.id_to_person.get("Alice")
        assert alice is not None

        self.assertEqual(alice.id, "Alice")
        self.assertEqual(alice.name, "Alice")
        self.assertEqual(alice.nickname, "Alice")
        self.assertIsNone(alice.email)
        self.assertEqual(alice.allowlist, [])
        self.assertEqual(alice.denylist, [])

    def test_valid_fields_maximal(self):
        data = yaml.safe_load(PEOPLE_MAXIMAL)
        people = _create_people_and_groups_info(data)
        alice = people.id_to_person.get("Alice")
        assert alice is not None

        self.assertEqual(alice.id, "Alice")
        self.assertEqual(alice.name, "Alice Ecila")
        self.assertEqual(alice.nickname, "Al")
        self.assertEqual(alice.email, "alice@eci.la")
        self.assertEqual(set(alice.allowlist), {"Alice", "Bob"})
        self.assertEqual(set(alice.denylist), {"Bob", "Eve"})


class GraphGenerationTesting(RondeTest):
    """Teste la construction du graphe (groupes, allow/denylist, erreurs) à partir de `PeopleAndGroups`."""

    def test_valid_data(self):
        data = yaml.safe_load(PEOPLE_MAXIMAL)
        people = _create_people_and_groups_info(data)
        try:
            # Alice ne peut offrir de cadeau à personne, mais ça n'est pas une erreur à ce stade
            graph = generate_people_graph(people)
        except GraphGenerationException as e:
            self.fail(e)
        self.assertEqual(graph["Alice"], [])

    def test_invalid_person_in_person_list(self):
        data = {
            "people": {
                "Alice": {},
                "Bob": {"denylist": ["Eve"]},  # Eve n'existe pas
            }
        }
        people = _create_people_and_groups_info(data)
        with self.assertRaises(GraphGenerationException) as context:
            generate_people_graph(people)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_LISTS)

    def test_invalid_person_in_groups(self):
        data = {
            "people": {
                "Alice": {},
                "Bob": {},
            },
            "groups": {
                "invalid_group": ["Eve"],  # Eve n'existe pas
            },
        }
        people = _create_people_and_groups_info(data)
        with self.assertRaises(GraphGenerationException) as context:
            generate_people_graph(people)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_CLUSTERS)

    def test_infinite_recursion(self):
        data = {
            "people": {
                "Alice": {},
                "Bob": {},
            },
            "groups": {
                "group_A": ["group_B"],
                "group_B": ["group_C"],
                "group_C": ["group_D"],
                "group_D": ["group_A"],
            },
        }
        people = _create_people_and_groups_info(data)
        with self.assertRaises(GraphGenerationException) as context:
            generate_people_graph(people)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.INFINITE_RECURSION)

    def test_group_name_also_person(self):
        data = {
            "people": {
                "Alice": {},
                "Bob": {},
            },
            "groups": {
                "Alice": ["Bob"],  # Alice est déjà une personne
            },
        }
        people = _create_people_and_groups_info(data)
        with self.assertRaises(GraphGenerationException) as context:
            generate_people_graph(people)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.GROUP_IS_ALSO_PERSON)

    def test_empty_list_of_people(self):
        data_A = {
            "people": {},
            "groups": {
                "group_A": [],
                "group_B": ["group_A"],
            },
        }
        data_B = {"people": {}}

        people_A = _create_people_and_groups_info(data_A)
        with self.assertRaises(GraphGenerationException) as context:
            generate_people_graph(people_A)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.PEOPLE_EMPTY)

        people_B = _create_people_and_groups_info(data_B)
        with self.assertRaises(GraphGenerationException) as context:
            generate_people_graph(people_B)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.PEOPLE_EMPTY)

    def test_random_seed(self):
        """Bon c'est pas opti.

        Dans l'idée on génère des graphes aléatoire, une fois sans seed et on regarde si tous les résultats
        sont différents, une fois avec et on regarde si tous les résultats sont pareils. SVP pas de jugement.
        """
        data = {
            "people": {
                "Alice": {},
                "Bob": {},
                "Carole": {},
                "Diana": {},
                "Ève": {},
                "Floréal": {},
                "Gargamel": {},
            },
        }
        pag = _create_people_and_groups_info(data)
        graph = generate_people_graph(pag)

        NB = 10
        SEED = 1337

        results_random = {hash(tuple(compute_hamiltonian_cycle(graph))) for _ in range(NB)}  # pyright: ignore[reportArgumentType]
        results_fixed = set()
        for _ in range(NB):
            random.seed(SEED)
            results_fixed.add(hash(tuple(compute_hamiltonian_cycle(graph))))  # pyright: ignore[reportArgumentType]

        self.assertEqual(len(results_random), NB)
        self.assertEqual(len(results_fixed), 1)
