"""Allow access to `examples` folder."""

import tempfile
import unittest
from pathlib import Path
from typing import override
from uuid import uuid4


class RondeTest(unittest.TestCase):
    examples: Path = Path(__file__).parent.parent / "examples"

    @property
    def example_people_yaml(self) -> str:
        return str(self.examples / "people.yaml")

    @property
    def example_people_csv(self) -> str:
        return str(self.examples / "people.csv")

    @property
    def example_mail(self) -> str:
        return str(self.examples / "mail.yaml")

    @property
    def example_message_html(self) -> str:
        return str(self.examples / "message.html")

    @classmethod
    def _get_file(cls, existing: bool, ext: str = "", content: str = "") -> str:
        name = Path(cls._tempdir_existing.name) / f"{uuid4().hex}{ext}"
        if existing:
            name.write_text(content, encoding="utf-8")
        return str(name)

    @classmethod
    def get_non_existing_file(cls, ext: str = "") -> str:
        return cls._get_file(False, ext)

    @classmethod
    def get_existing_file(cls, ext: str = "", content: str = "") -> str:
        return cls._get_file(True, ext, content)

    @classmethod
    @override
    def setUpClass(cls) -> None:
        cls._tempdir_existing = tempfile.TemporaryDirectory()
        cls._tempdir_non_existing = tempfile.TemporaryDirectory()
        return super().setUpClass()

    @classmethod
    @override
    def tearDownClass(cls) -> None:
        cls._tempdir_existing.cleanup()
        cls._tempdir_non_existing.cleanup()
        return super().tearDownClass()
