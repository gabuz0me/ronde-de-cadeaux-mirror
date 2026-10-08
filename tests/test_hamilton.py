import unittest

from ronde_de_cadeaux.tools import Graph, compute_hamiltonian_cycle


class HamiltonTesting(unittest.TestCase):
    def test_no_path(self):
        """Teste s'il est impossible de trouver un cycle hamiltonien."""
        data: Graph = {
            "A": ["B", "D", "A"],
            "B": ["A"],
            "C": ["A", "D"],
            "D": ["B", "C"],
        }
        for starter in data.keys():  # On teste chaque début, ça ne sert à rien mais on ne sait jamais.
            path = compute_hamiltonian_cycle(data, starter)
            self.assertIsNone(path)

    def test_yes_path(self):
        """Teste si on trouve un cycle hamiltonien."""
        data: Graph = {
            "A": ["B", "D", "A"],
            "B": ["A"],
            "C": ["A", "D", "B"],
            "D": ["B", "C"],
        }
        for starter in data.keys():  # On teste chaque début, ça ne sert à rien mais on ne sait jamais.
            path = compute_hamiltonian_cycle(data, starter)
            self.assertIsNotNone(path)
