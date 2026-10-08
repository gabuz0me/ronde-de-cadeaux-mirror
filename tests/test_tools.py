from unittest import TestCase

from ronde_de_cadeaux import tools


class ToolTesting(TestCase):
    data = ["1", 2, None, False]

    def test_shuffled(self):
        shuffled = tools.shuffled(self.data)
        self.assertEqual(set(self.data), set(shuffled))

    def test_path_as_tuples(self):
        result = [
            ("1", 2),
            (2, None),
            (None, False),
            (False, "1"),
        ]
        self.assertEqual(tools.list_as_cyclic_pairs(self.data), result)
