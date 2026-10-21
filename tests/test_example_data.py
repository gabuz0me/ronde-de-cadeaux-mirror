from pathlib import Path

from ronde_de_cadeaux._unique_yaml import unique_safe_load
from ronde_de_cadeaux.mail import _create_mail_info
from ronde_de_cadeaux.people_graph_generation import (
    create_people_and_groups_info,
    generate_people_graph,
)
from ronde_de_cadeaux.tools import compute_hamiltonian_cycle
from tests.base import RondeTest


class ExampleTest(RondeTest):
    """Teste la validation et la construction de `PeopleAndGroups` à partir de données brutes."""

    def test_people_data_yaml(self):
        """Teste si les données yaml fournies en exemple fonctionnent réellement."""
        try:
            pag = create_people_and_groups_info(Path(self.example_people_yaml))
            gra = generate_people_graph(pag)
            compute_hamiltonian_cycle(gra)
        except Exception as e:
            self.fail(e)

    def test_people_data_csv(self):
        """Teste si les données csv fournies en exemple fonctionnent réellement."""
        try:
            pag = create_people_and_groups_info(Path(self.example_people_csv))
            gra = generate_people_graph(pag)
            compute_hamiltonian_cycle(gra)
        except Exception as e:
            self.fail(e)

    def test_mail_config(self):
        """Teste si le fichier d'example de configuration mail est valide."""
        try:
            with open(self.example_mail_config) as file:
                data = unique_safe_load(file)
            _create_mail_info(True, data, None, True)
        except Exception as e:
            self.fail(e)
