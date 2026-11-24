import os
from unittest import TestCase
from unittest.mock import patch

from ronde_de_cadeaux import tools
from ronde_de_cadeaux.logger import Color, Style, colored


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

    def test_argparse_long_color(self):
        """Repère si dans une future version de Python la couleur par défaut des options longues d'`argparse` change.

        C'est pas zinzin, y'a en pratique aucun risque et c'est overkill mais bon, voilà quoi.
        """
        # https://github.com/python/cpython/blob/main/Lib/_colorize.py
        from _colorize import get_theme

        expected_prefix = get_theme(force_color=True).argparse.long_option

        # https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch.dict
        with patch.dict(os.environ, {"NO_COLOR": "0"}, clear=True):  # On désactive temporairement
            colored_text = colored("--option", Color.CYAN, Style.BOLD)
        self.assertTrue(colored_text.startswith(expected_prefix))  # Si le code de début est bon, ie la couleur, ça passe
