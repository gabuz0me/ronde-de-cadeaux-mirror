import tempfile
import unittest
from pathlib import Path
from typing import override
from uuid import uuid4

import email_validator

from ronde_de_cadeaux import logger


class RondeTest(unittest.TestCase):
    """Classe de base ayant accès au contenu du dossier contenant les exemples."""

    examples: Path = Path(__file__).parent.parent / "examples"

    @property
    def example_people_yaml(self) -> str:
        """Tout le monde a une adresse courriel ici."""
        return str(self.examples / "people.yaml")

    @property
    def example_people_csv(self) -> str:
        """Il y a des personnes sans adresse courriel."""
        return str(self.examples / "people.csv")

    @property
    def example_email_config(self) -> str:
        return str(self.examples / "email.yaml")

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
        email_validator.CHECK_DELIVERABILITY = False
        logger.logger.disabled = True
        return super().setUpClass()

    @classmethod
    @override
    def tearDownClass(cls) -> None:
        cls._tempdir_existing.cleanup()
        cls._tempdir_non_existing.cleanup()
        return super().tearDownClass()
