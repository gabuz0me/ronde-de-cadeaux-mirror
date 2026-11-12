"""Prevent yaml loading dict with non-unique values.

Many thanks to *ErichBSchulz*
https://gist.github.com/pypt/94d747fe5180851196eb?permalink_comment_id=3401011#gistcomment-3401011
"""

from typing import Any, Hashable, override

import yaml


class UniquenessError(Exception):
    pass


# special loader with duplicate key checking
class _UniqueKeyLoader(yaml.SafeLoader):
    @override
    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        mapping = []
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise UniquenessError(f"La clé '{key}' n'est pas unique")
            mapping.append(key)
        return super().construct_mapping(node, deep)


def unique_safe_load(stream: Any) -> Any:  # noqa: ANN401
    """Appelle `yaml.load` en garantissant que les clés d'un dictionnaire sont uniques.

    Peut lever une `UniquenessError` ou une `yaml.YAMLError`.
    """
    try:
        return yaml.load(stream, Loader=_UniqueKeyLoader)
    except UniquenessError:
        raise
    except yaml.YAMLError as e:
        if isinstance(e, yaml.MarkedYAMLError) and e.problem_mark is not None:
            raise yaml.YAMLError(f"YAML invalide : erreur à la ligne {e.problem_mark.line + 1}") from e
        raise yaml.YAMLError("YAML invalide") from e
