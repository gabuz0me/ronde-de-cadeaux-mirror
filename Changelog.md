<div align="center">

❖ [Français](#journal-des-modifications) ❖ [English](#changelog) ❖

</div>


---

<div align="center">

# Changelog

<img src="https://upload.wikimedia.org/wikipedia/commons/0/0b/English_language.svg" height="30" alt="EN"/>

</div>

- `0.0.0dev3`:
    - Using a real logger and adding a verbose/quiet mechanism alongside the `RONDE_DEBUG` env var.
    - i18n: Locale detection on Windows/Android/Gnunux and English translation

- `0.0.0dev2`:
    - Creating the changelog.
    - Better email-related error handling.

- `0.0.0dev1`:
    - Using `dacite` and `email-validator` instead of `pydantic` for schema validation.
    - Bugfix: People duplicates were not enforced in YAML.

- `0.0.0dev0`: Initial version based on the [legacy project](https://framagit.org/bertille-ddp/ronde-de-cadeaux). Added more unit tests, seed mechanism, data validation, template message when testing email config, template message format detection, and CSV people file. Properly packaged, can now be installed on PyPI.

---

<div align="center">

# Journal des modifications

<img src="https://upload.wikimedia.org/wikipedia/commons/f/f0/Flag_of_French_language.svg" height="30" alt="FR"/>

</div>

- `0.0.0dev3`:
    - Utilisation d'un réel logger et ajout d'un mécanisme de mode verbeux ou silencieux, utilisation de la variable d'environnement `RONDE_DEBUG` pour le logger.
    - i18n : Détection automatique de la langue sur Windows/Gnunux/Android et traduction de l'outil en anglais.

- `0.0.0dev2` :
    - Création du journal des modifications.
    - Meilleure gestion des erreurs concernant les courriels.

- `0.0.0dev1` :
    - Utilisation de `dacite` et de `email-validator` à la place de `pydantic` pour la validation de schémas.
    - Correction de bug : L'unicité des personnes n'était pas vérifiée en YAML.

- `0.0.0dev0` : Fondé sur le [projet initial](https://framagit.org/bertille-ddp/ronde-de-cadeaux). Ajout de tests unitaires, d'un mécanisme de graine aléatoire, de l'utilisation du message-type lors du test de la configuration du serveur de messagerie et de l'envoi des courriels, de la validation de schéma pour les fichiers de configuration, détection automatique des formats de fichiers, support du CSV pour le fichier des personnes. Proprement empaqueté et mis à disposition sur PyPI.