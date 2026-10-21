"""Prevent yaml loading dict with non-unique values.

Many thanks to *ErichBSchulz*
https://gist.github.com/pypt/94d747fe5180851196eb?permalink_comment_id=3401011#gistcomment-3401011
"""

from typing import Any, Hashable, override

import yaml


# special loader with duplicate key checking
class UniqueKeyLoader(yaml.SafeLoader):
    @override
    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        mapping = []
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            assert key not in mapping
            mapping.append(key)
        return super().construct_mapping(node, deep)


def unique_safe_load(stream: Any) -> Any:  # noqa: ANN401
    """Appelle `unique_safe_load` en garantissant que les clés d'un dictionnaire sont uniques."""
    try:
        res = yaml.load(stream, Loader=UniqueKeyLoader)
    except Exception:
        raise ValueError("""Uniqueness of key is broken""")
    return res
