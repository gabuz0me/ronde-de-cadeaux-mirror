import pathlib
import sys
import unittest

import yaml

root = pathlib.Path(__file__).parent.parent
sys.path.append(str(root))

from .graph_generation import GraphGenerationException, GraphGenerationExceptionType, generate_graph


class GraphGenerationTesting(unittest.TestCase):
    def test_example_data(self):
        """Teste si les données fournies en exemple fonctionnent réellement :D"""
        path = root / "examples/example_data.yaml"
        with open(path) as file:
            data = yaml.safe_load(file)
        generate_graph(data)

    def test_invalid_person_in_person_list(self):
        data = {
            "people": {
                "Alice": {},
                "Bob": {"denylist": ["Eve"]},  # Eve n'existe pas
            }
        }
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
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
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
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
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
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
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.CLUSTER_IS_ALSO_PERSON)

    def test_empty_list_of_people(self):
        data_A = {
            "people": {},
            "groups": {
                "group_A": [],
                "group_B": ["group_A"],
            },
        }
        data_B = {}

        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data_A)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.PEOPLE_EMPTY)

        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data_B)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.PEOPLE_EMPTY)
