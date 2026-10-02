import pathlib
import random
import sys
import unittest

import yaml

root = pathlib.Path(__file__).parent.parent
sys.path.append(str(root))

from .graph_generation import generate_graph
from .hamiltonian_path import hamilton


class HamiltonTesting(unittest.TestCase):
    def test_example_data(self):
        """Teste si les données fournies en exemple fonctionnent réellement :D"""
        path = root / "examples/example_data.yaml"
        with open(path) as file:
            data = yaml.safe_load(file)
        graph = generate_graph(data)
        path = hamilton(graph, random.choice(list(graph)))
        self.assertIsNotNone(path)

    def test_no_path(self):
        data = {
            "people": {
                "A": {"allowlist": ["B", "D"]},
                "B": {"allowlist": ["A"]},
                "C": {"allowlist": ["A", "D"]},
                "D": {"allowlist": ["B", "C"]},
            },
        }
        graph = generate_graph(data)
        path = hamilton(graph, "A")
        self.assertIsNone(path)
