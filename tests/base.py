"""Allow access to `examples` folder."""

import unittest
from pathlib import Path


class RondeTest(unittest.TestCase):
    examples: Path = Path(__file__).parent.parent / "examples"

    @property
    def people(self) -> str:
        return str(self.examples / "people.yaml")

    @property
    def mail(self) -> str:
        return str(self.examples / "mail.yaml")

    @property
    def message(self) -> str:
        return str(self.examples / "message.txt")

    @property
    def non_existing_file(self) -> str:  # Pas hyper propre en vrai
        p = self.examples / "output.txt"
        assert not p.exists()
        return str(p)

    @property
    def existing_file(self) -> str:
        return self.message  # Les tests ne vont pas écraser son contenu
