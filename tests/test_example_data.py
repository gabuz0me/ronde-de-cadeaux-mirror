import yaml

from ronde_de_cadeaux.graph_generation import (
    _create_people_and_groups_info,
    generate_people_graph_and_dict,
)
from ronde_de_cadeaux.mail import _create_mail_info
from ronde_de_cadeaux.tools import compute_hamiltonian_cycle
from tests.base import RondeTest


class ExampleTest(RondeTest):
    """Teste la validation et la construction de `PeopleAndGroups` à partir de données brutes."""

    def test_people_data(self):
        """Teste si les données fournies en exemple fonctionnent réellement."""
        try:
            with open(self.people) as file:
                data = yaml.safe_load(file)
            pag = _create_people_and_groups_info(data)
            gra = generate_people_graph_and_dict(pag)
            compute_hamiltonian_cycle(gra)
        except Exception as e:
            self.fail(e)

    def test_mail_config(self):
        """Teste si le fichier d'example de configuration mail est valide."""
        try:
            with open(self.mail) as file:
                data = yaml.safe_load(file)
            _create_mail_info(True, data, "", True, True)
        except Exception as e:
            self.fail(e)
