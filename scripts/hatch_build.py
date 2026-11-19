"""Build hook, ensures the .po files are translated into the .mo."""

from pathlib import Path
from subprocess import run
from typing import Any, override

from babel.messages.pofile import read_po
from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl

_RDC_DIR = Path(__file__).parent.parent / "ronde_de_cadeaux"
_LOCALE_DIR = _RDC_DIR / "locale"
_POT_DIR = _LOCALE_DIR / "ronde.pot"

_QUIET = True


# https://hatch.pypa.io/latest/plugins/builder/reference/
class I18nBuildHook(BuildHookInterface[BuilderConfig]):
    """Lance `pybabel extract`, `update` et `compile`.

    Si une erreur est détectée (par ex. une traduction marquée comme *fuzzy*), cela empêche le build.
    """

    PLUGIN_NAME = "i18n-hook"

    @override
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Super la fonction qu'est pas documentée, on était censé·e savoir où que `version` ça pouvait être `editable` ou `standard` ???"""  # noqa

        if version == "editable":
            print("Editable version, skipping i18n hook")
            return

        verbosity = "--quiet" if _QUIET else "--verbose"

        print("Running i18n hook...")
        ret_code = run(
            [
                "pybabel",
                verbosity,
                "extract",
                "--input-dirs",
                _RDC_DIR,
                "--output-file",
                _POT_DIR,
                "--no-wrap",
                "--omit-header",  # KISS
                "--no-location",  # Un peu de vie privée
            ]
        ).returncode

        if ret_code != 0:
            raise SystemExit("Error: Babel extraction failed.")

        ret_code = run(
            [
                "pybabel",
                verbosity,
                "update",
                "--input-file",
                _POT_DIR,
                "--output-dir",
                _LOCALE_DIR,
                "--no-wrap",
                "--ignore-pot-creation-date",
            ]
        ).returncode
        if ret_code != 0:
            raise SystemExit("Error: Babel update failed.")

        self.check_fuzzy_text()

        ret_code = run(
            [
                "pybabel",
                verbosity,
                "compile",
                "--directory",
                _LOCALE_DIR,
                "--domain",
                "messages i18nparse_patch",
            ]
        ).returncode
        if ret_code != 0:
            raise SystemExit("Error: Babel compile failed.")

        print("Success")

    # https://babel.pocoo.org/en/latest/api/messages/pofile.html
    def check_fuzzy_text(self) -> None:
        """Aaaah ça non! Pas de ça chez nous!!"""  # noqa
        for file in _LOCALE_DIR.glob("**/*.po"):
            with open(file, "r", encoding="utf-8") as f:
                catalog = read_po(f)
                for message in catalog:
                    if message.fuzzy:
                        raise SystemExit(f'In {file.name} ({catalog.locale}): Message "{message.id}" is fuzzy!')


@hookimpl
def hatch_register_build_hook() -> type[I18nBuildHook]:  # noqa
    return I18nBuildHook
