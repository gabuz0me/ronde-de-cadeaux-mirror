<div align=center>

# Ronde de Cadeaux

❖ **Français** ❖ [English](https://framagit.org/gabuzome/ronde-de-cadeaux/-/blob/main/README-en.md) ❖

[![Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fframagit.org%2Fgabuzome%2Fronde-de-cadeaux%2F-%2Fraw%2Fmain%2Fpyproject.toml&query=project.version&label=Version&color=green)](pyproject.toml) [![Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fframagit.org%2Fgabuzome%2Fronde-de-cadeaux%2F-%2Fraw%2Fmain%2Fpyproject.toml&query=project.requires-python&label=Python&color=FFD43B&logo=python&logoColor=FFD43B)](https://www.python.org/) [![PyPI](https://img.shields.io/badge/Download_on-PyPI-3775A9?logo=pypi&color=3775A9&logoSize=auto&logoColor=white)](https://pypi.org/project/ronde-de-cadeaux/)

[![Framagit](https://img.shields.io/badge/Framagit-725794?logo=gitlab&logoColor=FC6D26&logoSize=auto)](https://framagit.org/gabuzome/ronde-de-cadeaux/) [![GitHub](https://img.shields.io/badge/GitHub_mirror-181717?logo=github&logoSize=auto)](https://github.com/gabuz0me/ronde-de-cadeaux-mirror/)

</div>


---

**Ronde de Cadeaux** est un outil libre en ligne de commande pour tirer au sort des gens à qui faire des cadeaux façon *Secret Santa* ou *Noël Canadien*, envoyant des courriels aux participant⋅e⋅s pour leur indiquer la personne à régaler. Le tirage peut également être contrôlé par différents mécanismes de contraintes, comme par exemple empêcher une personne de tirer une personne spécifique ou faire en sorte qu'elle en tire une dans un groupe donné.

---

##### Table des matières

<!-- shd101wyy.markdown-preview-enhanced | VSCodium -->
<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=4 orderedList=false} -->
<!-- code_chunk_output -->

- [🤔 Comment qu'on s'en sert ?](#-comment-quon-sen-sert-)
  - [📥 Installation](#-installation)
  - [🧑‍💻 Utilisation](#-utilisation)
    - [🎁 Effectuer un tirage](#-effectuer-un-tirage)
    - [⚙️ Tester la configuration de l'envoi des courriels](#️-tester-la-configuration-de-lenvoi-des-courriels)
  - [📃 Format des différents fichiers d'entrée](#-format-des-différents-fichiers-dentrée)
    - [😎 Le fichier contenant les informations sur les gens](#-le-fichier-contenant-les-informations-sur-les-gens)
    - [📧 Le fichier de configuration de l'envoi des courriels](#-le-fichier-de-configuration-de-lenvoi-des-courriels)
    - [💬 Le fichier patron du message envoyé par courriel](#-le-fichier-patron-du-message-envoyé-par-courriel)
- [🥳 Exemples d'utilisation](#-exemples-dutilisation)
- [🔎 FAQ](#-faq)
- [🤓 Comment contribuer ou aider ?](#-comment-contribuer-ou-aider-)

<!-- /code_chunk_output -->

---

## 🤔 Comment qu'on s'en sert ?

### 📥 Installation

Cet outil est écrit en [Python](https://python.org/), assure-toi d'avoir installé une version **supérieure ou égale à la 3.12**. `ronde-de-cadeaux` s'installe en ligne de commande avec [*pip*](https://pypi.org/project/pip/) ou [*uv*](https://docs.astral.sh/uv/getting-started/installation/).

**Installation avec pip :**

```sh
pip install ronde-de-cadeaux
```

**Installation avec uv :**

```sh
uv tool install ronde-de-cadeaux
```

> [!tip] Astuce
> Utiliser une version de Python supérieure ou égale à la 3.14 permet d'avoir de la [couleur dans les messages d'aide](https://docs.python.org/3.14/library/argparse.html#color) 😎
### 🧑‍💻 Utilisation

Cet outil installe un seul exécutable, `ronde`. Voilà son message d'aide :

<!-- uv run cog -r -P  .\README* -->
<!--[[[cog
import os,sys;os.environ["COLUMNS"]="100";v=sys.version_info
if int(f"{v[0]}{v[1]}") < 314:
    raise Exception("cog Python>=3.14")
from ronde_de_cadeaux.parser import _makeParser as mp
print(f"```\n{mp().format_help().strip()}\n```")
]]]-->
```
Utilisation : ronde [-h] [--version] [-v | -q] [--test-email] [-a AUTH] [-m MESSAGE] [-p PEOPLE]
                    [-s] [-o OUTPUT] [--force] [--seed SEED]

Ce programme permet de générer un tirage de gens à qui offrir des cadeaux en prenant en compte un
système de contraintes complexes.

Arguments:
  -h, --help             Afficher ce message et quitter
  --version              Afficher le numéro de version du programme et quitter
  -v, --verbose          Active le mode verbeux
  -q, --quiet            Réduit les messages affichés
  --test-email           Tester la configuration de l'envoi des courriels
  -a, --auth AUTH        Fichier de configuration de l'envoi des courriels, voir la documentation
                         pour le schéma
  -m, --message MESSAGE  Fichier patron du message envoyé par courriel, voir la documentation pour
                         le schéma
  -p, --people PEOPLE    Fichier des personnes (YAML ou CSV, voir la documentation pour le schéma)
  -s, --show             Afficher la ronde calculée
  -o, --output OUTPUT    Fichier dans lequel exporter le tirage
  --force                Forcer l'écriture dans le fichier de sortie, même si celui-ci existe déjà
  --seed SEED            Graine aléatoire pour le tirage
```
<!--[[[end]]] (sum: k9zY32XuBx)-->

> [!important] Utilisation
> L'outil permet deux actions principales :
> - [Effectuer un tirage](#-effectuer-un-tirage).
> - [Tester la configuration de l'envoi des courriels](#️-tester-la-configuration-de-lenvoi-des-courriels).

> [!tip] Mode verbeux ou silencieux
> Le programme peut afficher plus ou moins de détail sur son fonctionnement, selon qu'on passe `--quiet` ou `--verbose`.

#### 🎁 Effectuer un tirage

Pour effectuer un tirage il faut fournir un fichier d'entrée contenant les informations sur les personnes participant au tirage, à minima leurs noms (et leurs adresses courriel si on envoie le tirage par courriel aux participant·e·s). Ce fichier est passé avec l'option `--people` et est au format CSV ou YAML. La structure de ce fichier est [discutée plus bas](#-le-fichier-contenant-les-informations-sur-les-gens).

Ensuite il faut effectuer au moins une des *actions* suivantes:

1. Envoyer un courriel aux participant·e·s en utilisant les options `--auth` suivi du *fichier de configuration de l'envoi des courriels* et `--message` suivi du *fichier patron du message envoyé par courriel* aux participant·e·s. Le détail de ces fichiers est [discuté plus bas](#-le-fichier-de-configuration-de-lenvoi-des-courriels), ainsi que les options supplémentaires relatives à cette action.
2. Afficher le tirage dans la console avec l'option `--show`.
3. Écrire le résultat du tirage dans un fichier avec l'option `--output` suivie d'un nom de fichier. Si le fichier existe déjà, une erreur survient mais il est possible de forcer le programme à écraser le fichier avec `--force`

> [!tip] Astuce
> Pour forcer un tirage aléatoire donnant systématiquement les mêmes résultats, il est possible de passer une *graine aléatoire* avec l'argument `--seed`. Cela permet par exemple de ne stocker en clair aucune information sur le tirage, mais d'être capable de le reproduire à l'identique dans le futur, si besoin est.

#### ⚙️ Tester la configuration de l'envoi des courriels

Avant d'envoyer un courriel à tout le monde, on peut vouloir s'assurer que 1. l’authentification au serveur de messagerie est correcte et que 2. le *fichier patron du message envoyé par courriel* est correct. Pour ce faire on utilise l'option `--test-email` en plus de l'option `--auth` vue plus haut. Cela se connecte aux serveurs de messagerie et envoie un courriel à l'adresse expéditrice utilisée pour envoyer les courriels. Si `--message` est passée, le message envoyé est celui du *fichier patron du message envoyé par courriel*, formaté avec des valeurs de test.

> [!warning] Attention
> Dans ce mode, le programme ne teste que la connexion au serveur de messagerie et si l'envoi de courriels est possible. Si le programme teste systématiquement si les adresses courriel sont valides et si les serveurs existent, il **n'envoie pas de courriel aux participant·e·s**. Il est recommandé de vérifier manuellement que les adresses courriels de tout le monde sont correctes et reçoivent bien les messages avant de procéder à un tirage.

### 📃 Format des différents fichiers d'entrée

#### 😎 Le fichier contenant les informations sur les gens

> [!note] Note
> Ce fichier peut être écrit au format [YAML](https://yaml.org/) ou [CSV](https://fr.wikipedia.org/wiki/Comma-separated_values). Il est passé en argument avec `--people`.

##### Le format CSV

> [!tip] Astuce
> Ce fichier est la façon la plus simple de réaliser un tirage où tout le monde peut piocher tout le monde, mais il n'offre aucune possibilité de contraintes ni de créer des champs personnalisés pour les personnes (ex. surnom). 

Ce type de fichier **doit** se terminer par l'extension `.csv` ou `.txt`, le séparateur est `;`. Voilà un exemple contenu d'un tel fichier (ou voir le [fichier d'exemple](examples/people.csv)) :

```
Alice Ecila ; alice@eci.la ; Alice la pote de Ève
Bœbélius    ;
Caroline
Ève         ;              ; Ève la pote d'Alice
```

Ici un tirage au sort sera effectué entre *Alice Ecila*, *Bœbélius*, *Caroline* et *Ève*. Chaque ligne représente une personne, commence par l'appellation de la personne, son (éventuelle) adresse courriel est indiquée après un points virgules `;`. D'éventuels commentaires sont insérés après le deuxième `;`. Les commentaires n'ont aucune influence sur le tirage.

Le fichier donné en exemple, s'il est valide pour les options `--show` et `--output` ne le sera évidemment pas pour l'option `--auth` puisque seule *Alice Ecila* possède une adresse courriel.

> [!note] Note
> Les espaces intermédiaires n'ont aucune influence sur les champs. Si la personne n'a pas d'adresse courriel, un `;` peut être inséré après son nom ou pas. Le fichier suivant est donc strictement équivalent à celui ci dessus :
> ```
> Alice Ecila; alice@eci.la; Alice la pote de Ève
> Bœbélius
> Caroline;
> Ève;;Ève la pote d'Alice
> ```

> [!warning] Attention
> Chaque personne doit avoir un nom différent...

##### Le format YAML

Ce type de fichier **doit** se terminer par l'extension `.yaml` ou `.yml`.

Ce type de fichier permet de personnaliser les champs ainsi que de créer des contraintes de tirage via les mécanismes de listes d'autorisation (*allowlist*) et de listes de rejet (*denylist*).

Un fichier YAML de description consiste en deux dictionnaires (notés avec des deux-points `:`), `people` et `groups` permettant de définir respectivement qui participe et les groupes de gens. Le second dictionnaire est optionnel et son utilité est [décrite plus bas](#les-groupes).

```yaml
# Structure de base de la configuration en YAML
people:
  ...
groups: # optionnel
  ...
```

###### Les gens


Les éléments de `people` sont eux aussi des dictionnaires, la clé étant l'appellation (ou identifiant) d'une personne, et les valeurs des champs décrivant la personne. Par exemple :

```yaml
people:
  Robert T:
    display_name: "Robert Trebor"
    nickname: "Bobby"
    email: "robert@trev.or"
```

Les champs `display_name` et `nickname` décrivent respectivement le nom à afficher et le surnom de la personne. Ils sont optionnels et valent par défaut l'identifiant de la personne, ici "Robert T". Ces champs servent essentiellement à mettre en forme le message type pour l'envoi des courriels. Le champ `email`, lui aussi optionnel désigne l'adresse courriel de la personne.

Le fichier de configuration YAML suivant est similaire à celui au format CSV vu plus haut :

```yaml
people:
  Alice Ecila: # Alice la pote de Ève
    email: "alice@eci.la"
  Bœbélius:
  Caroline:
  Ève: # Ève la pote d'Alice
```

> [!warning] Attention
> Notons que *Bœbélius*, *Caroline* et *Ève* n'ont pas de champs mais sont toujours des clés du dictionnaire `people`. Ils donc doivent avoir des `:` à la fin.

Le format YAML permet d'ajouter des contraintes via les mécanismes de listes d'autorisation via le champ `allowlist` et de listes de rejet via le champ `denylist`. Dans l'exemple suivant :

```yaml
people:
  A:
    allowlist:
    - B
    - C
  B:
    denylist:
    - A
  C:
    allowlist:
    - A
    - B
    denylist:
    - A
  D:
```

- *A* ne peut tirer que *B* ou *C*
- *B* ne peut pas tirer *A*
- *C* peut tirer "*A* et *B* mais pas *A*" donc seulement *B*
- *D* n'a aucune contrainte, il peut tirer tout le monde

Le cas de *C* n'a pas de sens pour le moment, pourquoi s'embêter à mettre une personne à la fois dans la liste d'autorisation et dans la liste de rejet ? Ce mécanisme prend tout son sens quand on ajoute le concept de groupes.

###### Les groupes

Le champ `groups` est lui aussi un dictionnaire et prend en clé un nom de groupe et en valeur une liste de personnes. Prenons par exemple deux familles, les *Ecila* et les *Trebor*. *Alice E*, *Ève* et *Dorian* font partie de la famille *Ecila* et *Robert*, *Alice T* et *Fatma*. Supposons que chaque famille fait déjà une [ronde de cadeaux](https://framagit.org/gabuzome/ronde-de-cadeaux/) dans son coin et souhaite faire tirage de sorte qu'une personne d'une famille ne puisse pas tirer quelqu'un·e de sa propre famille pour éviter un cas où une personne doit offrir un cadeaux deux fois à la même personne. Maintenant supposons que *Dorian* ne connaisse pas très bien *Alice T* et qu'on souhaite faire en sorte qu'il ne puisse pas la tirer. Tout ceci est facilement modélisable, par exemple comme ceci :

```yaml
people:

  # Famille Ecila
  Alice E:
    denylist: [Ecila]
  Ève:
    denylist: [Ecila]
  Dorian:
    denylist: [Ecila, Alice T] # Dorian ne peut tirer personne de sa famille ni `Alice T`

  # Famille Trebor
  Robert:
    denylist: [Trebor]
  Alice T:
    denylist: [Trebor]
  Fatma:
    allowlist: [Ecila] # À deux groupes, équivalent à mettre Trebor dans sa denylist

groups:
  Ecila: [Alice E, Ève, Dorian]
  Trebor: [Robert, Alice T, Fatma]
```

En effet ici, dans `groups` on définit deux groupes, les familles *Trebor* et *Ecila*, et dans les `allowlist` et `denylist` des personnes on ajoute ces contraintes.

> [!tip] Astuce
> Notons qu'en YAML les listes peuvent être définies avec la syntaxe de liste à puce et celle utilisant des crochets, voir les deux précédents exemples.

> [!important] Résumé des contraintes
> - Les **personnes** définies dans `people` peuvent avoir des champs `allowlist` et `denylist`.
> - Chacun de ces champs est une liste contenant les identifiants de **personnes** ou de **groupe**.
> - Les **groupes** définis dans `groups` contiennent une liste de **personnes** ou de **groupes** .
> - Par défaut, si une **personne** n'a pas de `allowlist`, on considère qu'elle peut tirer tout le monde.
> - L'ensemble des **personnes** qu'une **personne** peut tirer est définie comme l'ensemble des gens contenus dans sa `allowlist` (ou voir règle précédente) moins l'ensemble des gens contenus dans sa `denylist`.

> [!note] Note
> Voir le [fichier donné en exemple](examples/people.yaml) pour un exemple complexe d'architecture de groupes et de personnes.

#### 📧 Le fichier de configuration de l'envoi des courriels

Le *fichier de configuration de l'envoi des courriels* est un fichier au format YAML. Il est passé avec l'argument `--auth`. Il est structuré comme suit:

- `smtp`: (Paramètres du serveur SMTP)
  - `hostname`: Adresse du serveur SMTP, obligatoire.
  - `port`: Port du serveur SMTP, optionnel et vaut `587` par défaut.
- `imap`: (Paramètres du serveur IMAP, optionnel)
  - `hostname`: Adresse du serveur IMAP, optionnelle et vaut `smtp.hostname` par défaut.
  - `port`: Port du serveur IMAP, optionnel et vaut `143` par défaut.
  - `sent_folder`: Nom du dossier des courriels envoyés, optionnel et vaut `Sent` par défaut.
- `username`: Identifiant de connexion, obligatoire.
- `password`: Mot de passe pour la connexion, demandé lors de l'exécution du programme si non fourni.
- `sender_email`: Adresse courriel expéditrice, optionnelle et vaut `username` par défaut.
- `sender_name`: Nom associé à l'adresse courriel expéditrice, optionnel et vaut `username` par défaut.
- `copy_to_sent_folder`: Est-ce que le courriel envoyé doit également être copié dans le dossier des courriels envoyés, optionnel, `true` par défaut.
- `body_text_format`: Formatage du *fichier de configuration de l'envoi des courriels*, à valeur dans {`auto`, `txt` ou `html`}. Un courriel peut en effet être un texte pur ou bien un document au format HTML. Par défaut vaut `auto`, ce qui laisse le programme déduire le formatage à utiliser selon l'extension du fichier. (Il y a très peu de raisons de vouloir toucher à ce paramètre)

Un fichier minimal ressemble à :

```yaml
smtp:
  hostname: "my_email_server.org"
username: "my_email@domain.ext"
```

> [!tip] Astuce
> Un fichier plus détaillé est [donné en exemple](examples/email.yaml).

> [!warning] Attention
> Ce programme se connecte au serveur de messagerie en *STARTTLS*. Ce protocole n'est pas supporté par tous les serveurs.

#### 💬 Le fichier patron du message envoyé par courriel

Ce fichier est obligatoirement utilisé pour l'envoi des courriels. Il est passé en argument avec `--message`. C'est un modèle ou patron de conception (*template*) dont certains champs vont être automatiquement remplacés par les informations concernant cellui qui offre et cellui qui reçoit.

Ce message peut être au format texte brut ou HTML. Le format est déduit par défaut via l'extension du fichier (`.txt` ou `.html`).

Voici un exemple de fichier type au format HTML :

```html
{gifter_name}, cette année tu feras un cadeau à…

Salut {gifter_nickname} !<br>
La personne qui t'a été attribuée lors du tirage est <b>{giftee_name}</b>.<br><br>

On se voit le 13/12 chez Camille ;) 
```

La première ligne définit le sujet du message, les autres le corps du message. Il peut y avoir des lignes blanches entre les deux parties, cela ne fait aucune différence.

Les remplacements par personnes seront fait comme suit, sur la base des informations des personnes :

| Champ | Valeur |
|---|---|
| `{sender_email}` | Adresse courriel expéditrice |
| `{sender_name}` | Nom associé à l'adresse expéditrice |
| `{gifter_id}` | Identifiant de la personne qui reçoit le courriel |
| `{gifter_name}` | Nom de la personne qui reçoit le courriel |
| `{gifter_nickname}` | Surnom de la personne qui reçoit le message |
| `{gifter_email}` | Adresse courriel de la personne qui reçoit le courriel |
| `{giftee_id}` | Identifiant de la personne tirée au sort |
| `{giftee_name}` | Nom de la personne tirée au sort |
| `{giftee_nickname}` | Surnom de la personne qui reçoit le message |
| `{giftee_email}` | Adresse courriel de la personne tirée au sort |

> [!note] Note
> En pratique, seuls les champs `gifter_name`, `gifter_nickname`, `giftee_name` et `giftee_nickname` sont utiles, mais le reste est disponible si besoin.

> [!important] Important
> Si ce fichier est passé en option lors du test de l'envoi des courriels (avec `--test-email`), un courriel est envoyé à l'adresse d'envoi avec des valeurs de test pour les champs à remplacer.

## 🥳 Exemples d'utilisation

Effectuer un tirage avec les données fournies en exemple avec la graine aléatoire `jaaj42`, les exporter dans un fichier `tirage.txt` qui existait déjà et afficher ce tirage dans la console :

```sh
ronde -p examples/people.yaml -o tirage.txt --force -s --seed jaaj42
Alice-Andréa-Alexia Foo → Isöbel Bar
             Isöbel Bar → Dave Foo
               Dave Foo → Henry Bar
              Henry Bar → Cärol Foo
              Cärol Foo → Eve Bar
                Eve Bar → Linda Qux
              Linda Qux → Gulliver Bar
           Gulliver Bar → Nick Qux
               Nick Qux → Flora Bar
              Flora Bar → Jack Baz
               Jack Baz → Bœbélius Foo
           Bœbélius Foo → Mark Qux
               Mark Qux → Alice-Andréa-Alexia Foo
```

Tester la connection au serveur de messagerie avec un message type :

```sh
ronde --test-email -a examples/email.yaml -m examples/message.html
```

## 🔎 FAQ

> Pourquoi j'utiliserais un outil chelou en ligne de commande comme ça plutôt qu'un site tout fait qui s'occupe de tout ?

Bonne question, voilà des pistes de réflexions en vrac :

- Tu ne donnes pas tes données personnelles ni celles de tes proches à un tiers dont tu en ignores l'usage...
- Les sites ne gèrent pas (tous) un système de contrainte comme celui proposé qui permet de faire des tirages complexes, s'assurant par exemple que les couples ne se tirent pas entre eux, que les enfant ne puissent pas tirés d'adultes de la famille trop éloignée, tout ça.
- C'est stylé la ligne de commande en vrai, non ?
- Vive le logiciel libre !

> C'est un peu une usine à gaz ton truc. Moi j'ai juste un groupe de potes sans contraintes particulières.

Le [format CSV](#le-format-csv) est parfait pour ce genre de cas 😉

> Je veux faire un tirage pour ma famille de manière à ce que les adultes se tirent entre eux et les enfants entre eux, comment je fais ?

Cet outil génère un cycle hamiltonien, c'est à dire une boucle unique qui passe par toutes les personnes impliquées. Dans le cas proposé là, l'outil ne trouvera aucune solution, et affichera un message d'erreur. En effet la solution serait d'avoir deux cycles, un pour les adultes et un pour les enfants. Dans ce cas, il faudra faire deux tirages. Plus généralement, si il y a *N* sous-groupes qui n'interagissent pas les uns avec les autres, il faudra faire *N* tirages.

La possibilité de permettre à l'outil de générer le nombre minimal de cycles hamiltoniens est en cours de réflexion, mais c'est un problème difficile qui n'a peut être pas énormément de cas d'usage réels.

> [!warning] Attention
> Pour résumer, le programme ne peut pas (encore ?) générer un tirage qui engendrerait plusieurs boucles entre les gens.

## 🤓 Comment contribuer ou aider ?

##### Aider le projet

Déjà il n'y a pas besoin de savoir développer pour contribuer : tous les retours sont les bienvenus, que ce soient les problèmes ou les idées d'améliorations. Pour faire un retour, contacte-moi par courriel ou mieux, si tu as un compte framagit, [crée un ticket](https://framagit.org/gabuzome/ronde-de-cadeaux/-/issues/new).

##### Développer

###### Installation en mode développement

Si tu veux absolument développer il te faudra cloner le projet avec [`git`](https://git-scm.com/) :

```sh
git clone git@framagit.org:gabuzome/ronde-de-cadeaux.git ronde_de_cadeaux/
cd ronde_de_cadeaux/
```

Dans le dossier du projet, tu installes le packet avec `pip` ou `uv` dans un [environnement virtuel](https://docs.python.org/3/library/venv.html) :

Avec `pip` :
```sh
# 1. Création de l'environnement virtuel
python -m venv .venv

# 2. Activation dudit environnement virtuel
    # Sous Windows :
.venv/Scripts/Activate.ps1
    # Sous Gnunux :
source .venv/bin/activate

# 3. Installation en mode éditable avec le groupe `dev` dans l'environnement
pip install -e . --group dev
```

Avec `uv` :

```sh
uv sync
```

Une fois l'environnement activé dans le terminal, l'exécutable `ronde` prend en compte les modifications en temps réel.

###### Modifier le code

Avant de faire une merge request, n'hésite pas à créer des tests unitaires pour t'assurer que tout fonctionne. Et il te faudra lancer tous les autres tests unitaires pour s'assurer de n'avoir rien cassé :

```sh
python -m unittest discover -s tests
```

Il faudra aussi valider le code avec [`basedpyright`](https://docs.basedpyright.com/latest/) et [`ruff`](https://docs.astral.sh/ruff/), qu'on peut facilement installer avec :

```sh
# Installation avec pip ou uv
pip install -e . --group quality
uv sync --group quality

# Formatage et validation
ruff check --select I --fix # S'assurer que tous les imports sont triés alphabétiquement
ruff format # Formatter le code
basedpyright # S'assurer que le static type checker ne détecte aucune anomalie
```
> [!tip] Astuce
> Le plus simple est d'utiliser [Visual Studio Code](https://code.visualstudio.com/) (ou mieux [VSCodium](https://vscodium.com/)) : un `.vscode/` existe pour simplifier le lancement des tests et le debug, et cela permet d'automatiser `ruff` et `basedpyright` en proposant les modules adéquats.

Des pistes de trucs en vrac qui pourraient être chouette :

- Résoudre le problème de la couverture minimale du graphe par des cycles hamiltoniens.
- Traduire le projet dans plus de langues
- Faire de la GUI

> [!important] ❤️
> Si vraiment tu as envie de donner de la bonne THUNE pour ce projet, déjà incroyable et merci, mais je n'en n'ai pas besoin donc donne plutôt aux associations qui œuvrent pour des causes justes, au hasard la [LPO 🐦](https://www.lpo.fr/), [La Quadrature du Net 🥧](https://www.laquadrature.net/), [Amnesty International 🕯️](https://www.amnesty.org/) ou l'[Association France Palestine Solidarité 🍉](https://www.france-palestine.org/)...

---

Ce projet est la continuation du projet [ronde-de-cadeaux originel](https://framagit.org/bertille-ddp/ronde-de-cadeaux).