import pathlib
import sys
import unittest
import yaml

root = pathlib.Path(__file__).parent.parent
sys.path.append(str(root))

from src.graph_generation import generate_graph, GraphGenerationException, GraphGenerationExceptionType


class GraphGenerationTesting(unittest.TestCase):

    def test_example_data(self):
        """Teste si les données fournies en exemple fonctionnent réellement :D"""
        path = root / 'examples/example_data.yaml'
        with open(path) as file:
            data = yaml.safe_load(file)
        generate_graph(data)

    def test_invalid_person_in_person_list(self):
        data = {
            'people': {
                "Alice": {},
                "Bob": {'denylist' : ["Eve"]}, # Eve n'existe pas
            }
        }
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_LISTS)

    def test_invalid_person_in_clusters(self):
        data = {
            'people': {
                "Alice": {},
                "Bob": {},
            },
            'clusters': {
                'invalid_cluster': ['Eve'], # Eve n'existe pas
            }
        }
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.UNDEFINED_CONSTRUCTING_CLUSTERS)

    def test_infinite_recursion(self):
        data = {
            'people': {
                "Alice": {},
                "Bob": {},
            },
            'clusters': {
                'cluster_A': ['cluster_B'],
                'cluster_B': ['cluster_C'],
                'cluster_C': ['cluster_D'],
                'cluster_D': ['cluster_A'],
            }
        }
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.INFINITE_RECURSION)

    def test_cluster_name_also_person(self):
        data = {
            'people': {
                "Alice": {},
                "Bob": {},
            },
            'clusters': {
                'Alice': ['Bob'], # Alice est déjà une personne
            }
        }
        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.CLUSTER_IS_ALSO_PERSON)

    def test_empty_list_of_people(self):
        data_A = {
            'people': {
            },
            'clusters': {
                'cluster_A': [],
                'cluster_B': ['cluster_A'],
            }
        }
        data_B = {}

        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data_A)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.PEOPLE_EMPTY)

        with self.assertRaises(GraphGenerationException) as context:
            generate_graph(data_B)
        self.assertEqual(context.exception.type, GraphGenerationExceptionType.PEOPLE_EMPTY)