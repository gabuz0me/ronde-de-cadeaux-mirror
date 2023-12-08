#!/usr/bin/env python3

"""
En l'an de grâce 2023, au huitième (8) jour du dernier mois (12) du calendrier grégorien alors en vogue,
la structure de données pour créer des personnes et des groupes changea irrémédiablement :
En effet, pourquoi s'ennuyer avec des "groupes de personnes" et des "groupes de groupes" dans la création
des groupes ?, et pourquoi créer une allow list de groupes et une de personnes (idem deny list) quand on peut
mélanger les deux ? En fait, une personne peut être vue comme un groupe ne contenant qu'elle. Il devrait
donc être possible d'écrire par exemple :

# data.yaml
people:
  Eve Bar:
    email: "eve@bar.me"
    denylist: ["Flora Bar", "Cousinade2023", "Bob le bricolo", "Famille côté Yvonne"]
  ...

Et le monde s'en porterait mieux.

Ce script permet de convertir un fichier yaml pré-2023/12/08 en une version post-2023/12/08.
(Peut-être qu'un jour un système de version plus efficace existera ? Ce script ne raconte pas cette histoire.)

Utilisation : ./data_converter_2023_12_08.py ton_vieux_fichier_ici.yaml [un_autre_vieux_fichier.yaml ...]
"""

import sys
import yaml
import pathlib

def process(file_path: str):
    data = None

    processed_data = {}
    processed_data_people = {}
    processed_data_clusters = {}

    i_path = pathlib.Path(file_path)
    o_path = str(i_path.parent / i_path.stem) + '_updated' + i_path.suffix
    print(f"Traitement de {i_path}... ", end='')

    try:
        with open(i_path, encoding='utf-8') as file:
            data = yaml.safe_load(file)
    except:
        print(f"Impossible à charger")
        return

    people_data = data.get('people')
    if people_data is not None:
        for person, info in people_data.items():
            processed_data_people[person] = {}
            for key in ['display_name', 'nickname', 'email']:
                if key in people_data[person]:
                    processed_data_people[person][key] = people_data[person][key]

            allowlist_p = info.get('allowlist', [])
            allowlist_c = info.get('allowlist_clusters', [])
            denylist_p = info.get('denylist', [])
            denylist_c = info.get('denylist_clusters', [])

            allowlist = set([*allowlist_c, *allowlist_p])
            if len(allowlist) != len(allowlist_c) + len(allowlist_p):
                print(f"Erreur :\n  - Un groupe à le même nom qu'une personne dans les allowlists de '{key}'")
                return
            denylist = set([*denylist_c, *denylist_p])
            if len(denylist) != len(denylist_c) + len(denylist_p):
                print(f"Erreur :\n  - Un groupe à le même nom qu'une personne dans les denylists de '{key}'")
                return

            if len(allowlist) != 0 : processed_data_people[person]['allowlist'] = list(allowlist)
            if len(denylist) != 0 : processed_data_people[person]['denylist'] = list(denylist)
        processed_data['people'] = processed_data_people

    cluster_data = data.get('clusters')
    if cluster_data is not None:
        for cluster in cluster_data.keys():
            p_list = cluster_data[cluster].get('people', [])
            c_list = cluster_data[cluster].get('subclusters', [])

            if len(p_list) + len(c_list) == 0:
                continue # cluster vide : on saute

            processed_data_clusters[cluster] = [*p_list, *c_list]
        processed_data['clusters'] = processed_data_clusters

    with open(o_path, 'w', encoding='utf-8') as file:
        yaml.dump(processed_data, file, sort_keys=False, allow_unicode=True)

    print(f"Exporté !")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Utilisation : ./data_converter_2023_12_08.py ton_vieux_fichier_ici.yaml [un_autre_vieux_fichier.yaml ...]")
        exit()

    for file_path in sys.argv[1:]:
        process(file_path)