<div align="center">

❖ [Français](#journal-des-modifications) ❖ [English](#changelog) ❖

</div>


---

<div align="center">

# Changelog

<img src="https://upload.wikimedia.org/wikipedia/commons/0/0b/English_language.svg" height="30" alt="EN"/>

</div>

- `0.0.0dev2`:
    - Creating the changelog

- `0.0.0dev1`:
    - Using `dacite` and `email-validator` instead of `pydantic` for schema validation.
    - Bugfix: People duplicates were not enforced in YAML

- `0.0.0dev0`: Initial version based on the [legacy project](https://framagit.org/bertille-ddp/ronde-de-cadeaux). Added more unit tests, seed mechanism, data validation, template message when mail testing, template message format detection, and CSV people file. Properly packaged, can now be installed on PyPI.

---

<div align="center">

# Journal des modifications

<img src="https://upload.wikimedia.org/wikipedia/commons/f/f0/Flag_of_French_language.svg" height="30" alt="FR"/>

</div>

- `0.0.0dev2`:
    - Création du journal des modifications

- `0.0.0dev1` :
    - Utilisation de `dacite` et de `email-validator` à la place de `pydantic` pour la validation de schémas.
    - Correction de bug : L'unicité des personnes n'était pas vérifiée en YAML.

- `0.0.0dev0` : Fondé sur le [projet initial](https://framagit.org/bertille-ddp/ronde-de-cadeaux). Ajout de tests unitaires, d'un mécanisme de graine aléatoire, de l'utilisation du message-type lors du test de l’authentification mail, de la validation de schéma pour les fichiers de configuration, détection automatique des formats de fichiers, support du CSV pour le fichier des personnes. Proprement empaqueté et mis à disposition sur PyPI.