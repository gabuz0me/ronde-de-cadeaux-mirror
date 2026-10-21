<div align=center>

# Ronde de Cadeaux

❖ **Français** ❖ [English](https://framagit.org/gabuzome/ronde-de-cadeaux/-/blob/main/README-en.md) ❖

[![Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fframagit.org%2Fgabuzome%2Fronde-de-cadeaux%2F-%2Fraw%2Fmain%2Fpyproject.toml&query=project.version&label=Version&color=green)](pyproject.toml) [![Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fframagit.org%2Fgabuzome%2Fronde-de-cadeaux%2F-%2Fraw%2Fmain%2Fpyproject.toml&query=project.requires-python&label=Python&color=FFD43B&logo=python&logoColor=FFD43B)](https://www.python.org/) [![PyPI](https://img.shields.io/badge/Download_on-PyPI-3775A9?logo=pypi&color=3775A9&logoSize=auto&logoColor=white)](https://pypi.org/project/ronde-de-cadeaux/)

[![Framagit](https://img.shields.io/badge/Framagit-725794?logo=gitlab&logoColor=FC6D26&logoSize=auto)](https://framagit.org/gabuzome/ronde-de-cadeaux/) [![GitHub](https://img.shields.io/badge/GitHub_mirror-181717?logo=github&logoSize=auto)](https://github.com/gabuz0me/ronde-de-cadeaux-mirror/)

</div>


---

**Ronde de Cadeaux** est un outil libre en ligne de commande pour tirer au sort des gens à qui faire des cadeaux façon *Secret Santa* ou *Noël Canadien*, envoyant des mails aux participant⋅e⋅s pour leur indiquer la personne à régaler. Le tirage peut également être contrôlé par différents mécanismes de contraintes, comme par exemple empêcher une personne de tirer une personne spécifique ou faire en sorte qu'elle en tire une dans un groupe donné.

---

##### Table des matières

<!-- shd101wyy.markdown-preview-enhanced | VSCodium -->
<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=4 orderedList=false} -->
<!-- code_chunk_output -->

- [🤔 Comment qu'on s'en sert ?](#-comment-quon-sen-sert-)
  - [📥 Installation](#-installation)
  - [🧑‍💻 Utilisation](#-utilisation)
    - [🎁 Effectuer un tirage](#-effectuer-un-tirage)
    - [⚙️ Tester la configuration mail](#️-tester-la-configuration-mail)
  - [📃 Format des différents fichiers d'entrée](#-format-des-différents-fichiers-dentrée)
    - [😎 Le fichier contenant les informations sur les gens](#-le-fichier-contenant-les-informations-sur-les-gens)
    - [📧 Le fichier de configuration mail](#-le-fichier-de-configuration-mail)
    - [💬 Le fichier type de message](#-le-fichier-type-de-message)
- [🥳 Exemples d'utilisation](#-exemples-dutilisation)
- [🔎 FAQ](#-faq)
- [🤓 Comment contribuer ou aider ?](#-comment-contribuer-ou-aider-)

<!-- /code_chunk_output -->

---

## 🤔 Comment qu'on s'en sert ?

### 📥 Installation

Cet outil est écrit en [Python](https://python.org/) 3.12, assure-toi d'avoir installé une version supérieure ou égale à la 3.12. Ronde-de-cadeaux s'installe en ligne de commande avec [*pip*](https://pypi.org/project/pip/) ou [*uv*](https://docs.astral.sh/uv/getting-started/installation/).

**Installation avec pip :**

```bash
pip install ronde-de-cadeaux
```

**Installation avec uv :**

```bash
uv tool install ronde-de-cadeaux
```

### 🧑‍💻 Utilisation

Cet outil installe un seul exécutable, `ronde`. Voilà son message d'aide :
<!-- Terminal size: 100 -->
``` 
Utilisation : ronde [-h] [--version] [--test-mail] [-a AUTH] [-m MESSAGE] [--no-imap]
                    [--text-format {html,txt,auto}] [-p PEOPLE] [-s] [-o OUTPUT] [--force]
                    [--seed SEED]

Ce programme permet de générer un tirage de gens à qui offrir des cadeaux en prenant en compte un
système de contraintes complexes.

Arguments:
  -h, --help            Afficher ce message et quitter
  --version             Afficher le numéro de version et quitter
  --test-mail           Tester la configuration de mail
  -a AUTH, --auth AUTH  Fichier de configuration mail
  -m MESSAGE, --message MESSAGE
                        Fichier patron du message envoyé par mail
  --no-imap             Ne pas copier les mails dans la boîte d'envoi
  --text-format {html,txt,auto}
                        Formatage du corps du mail (par défaut `auto`, essaye de détecter)
  -p PEOPLE, --people PEOPLE
                        Fichier des personnes (YAML ou CSV, voir la documentation pour le schéma)
  -s, --show            Afficher la ronde calculée
  -o OUTPUT, --output OUTPUT
                        Fichier dans lequel exporter le tirage
  --force               Forcer l'écriture dans le fichier de sortie, même si celui-ci existe déjà
  --seed SEED           Utilise cette graine aléatoire pour le tirage
```

L'outil permet deux actions principales, [effectuer un tirage](#-effectuer-un-tirage) et [tester la configuration mail](#️-tester-la-configuration-mail).

#### 🎁 Effectuer un tirage

Pour effectuer un tirage il faut fournir un fichier d'entrée contenant les informations sur les personnes participant au tirage, à minima leurs noms (et leur mails si on envoie le tirage par mail aux participant·e·s). Ce fichier est passé avec l'option `--people` et est au format CSV ou YAML. La structure de ce fichier est [discutée plus bas](#-le-fichier-contenant-les-informations-sur-les-gens).

Ensuite il faut effectuer au moins une des actions suivantes:

1. Envoyer un mail aux participant·e·s en utilisant les options `--auth` suivi du fichier de configuration mail et `--message` suivi message type à envoyer aux participant·e·s. Le détail de ces fichiers est [discuté plus bas](#-le-fichier-de-configuration-mail), ainsi que des options supplémentaires à l'action d'envoi de mail.
2. Afficher le tirage dans la console avec l'option `--show`.
3. Écrire le résultat du tirage dans un fichier avec l'option `--output` suivie d'un nom de fichier. Si le fichier existe déjà, une erreur survient mais il est possible de forcer le programme à écraser le fichier avec `--force`

Pour forcer un tirage aléatoire donnant systématiquement les mêmes résultats, il est possible de passer une *graine aléatoire* avec l'argument `--seed`. Cela permet par exemple de ne stocker en clair aucune information sur le tirage, mais d'être capable de le reproduire à l'identique dans le futur, si besoin il est.

#### ⚙️ Tester la configuration mail

Avant d'envoyer un mail à tout le monde, on peut vouloir s'assurer que 1. l’authentification mail est correcte et que 2. le message type est correctement formaté. Pour ce faire on utilise l'option `--test-mail` en plus de l'option `--auth` vue plus haut. Cela se connecte aux serveurs mail et envoie un mail à l'adresse mail utilisée pour envoyer les mails. Si `--message` est passée, le message envoyé est formaté avec des valeurs de test.

### 📃 Format des différents fichiers d'entrée

#### 😎 Le fichier contenant les informations sur les gens

Ce fichier peut être écrit au format [YAML](https://yaml.org/) ou [CSV](https://fr.wikipedia.org/wiki/Comma-separated_values). Il est passé en argument avec `--people`.

##### Format CSV

Ce type de fichier **doit** se terminer par l'extension `.csv` ou `.txt`, le séparateur est `;`. Voilà un exemple contenu d'un tel fichier (ou voir le [fichier d'exemple](examples/people.csv)) :

```
Alice Ecila  ; alice@eci.la ; Alice la pote de Ève
Bœbélius            ;
Caroline
Ève ; ; Ève la pote d'Alice
```

Ici un tirage au sort sera effectué entre *Alice Ecila*, *Ben*, *Bœbélius* et *Caroline*. Chaque ligne représente une personne, commence par l'appellation de la personne et son (éventuelle) adresse mail est indiquée après un points virgules `;`. D'éventuels commentaires sont insérés après le deuxième `;`. Les commentaires n'ont aucune influence sur le tirage. Les espaces intermédiaires non plus et si la personne n'a pas d'adresse mail, un `;` peut être inséré après son nom ou pas. Il va sans dire que chaque personne doit avoir un nom différent.

Ce fichier est la façon la plus simple de réaliser un tirage mais n'offre aucune possibilité de contraintes ni de créer des champs personnalisés pour les personnes (ex. surnom).

Le fichier donné en exemple, s'il est valide pour les options `--show` et `--output` ne le sera évidemment pas pour l'option `--auth` puisque seule *Alice Ecila* possède une adresse mail.

##### Le format YAML

Ce type de fichier **doit** se terminer par l'extension `.yaml` ou `.yml`.

Ce type de fichier permet de personnaliser les champs ainsi que de créer des contraintes de tirage via les mécanismes de listes d'autorisation (*allowlist*) et de listes de rejet (*denylist*).

Un exemple de fichier est [donné en exemple](/examples/people.yaml).

Un fichier yaml de description consiste en deux dictionnaires (notés avec des deux-points `:`), `people` et `groups` permettant de définir respectivement qui participe et les groupes de gens. Le second dictionnaire est optionnel et son utilité est [décrite plus bas](#les-groupes).

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

Les champs `display_name` et `nickname` décrivent respectivement le nom à afficher et le surnom de la personne. Ils sont optionnels et valent par défaut l'identifiant de la personne, ici "Robert T". Ces champs servent essentiellement à mettre en forme le message type pour l'envoi des mails. Le champ `email`, lui aussi optionnel désigne l'adresse mail de la personne.

Le fichier de configuration YAML suivant est similaire à celui au format CSV vu plus haut :

```yaml
people:
  Alice Ecila: # Alice la pote de Ève
    email: "alice@eci.la"
  Bœbélius:
  Caroline:
  Ève: # Ève la pote d'Alice
```

Notons que *Bœbélius*, *Caroline* et *Ève* n'ont pas de champs mais sont toujours des clés de dictionnaire et donc doivent avoir des `:` à la fin.

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

Notons qu'en YAML les listes peuvent être définies avec la syntaxe de liste à puce et celle utilisant des crochets, voir les deux précédents exemples.

###### Résumé des contraintes

- Les **personnes** définies dans `people` peuvent avoir des champs `allowlist` et `denylist`.
- Chacun de ces champs est une liste contenant les identifiants de **personnes** ou de **groupe**.
- Les **groupes** définis dans `groups` contiennent une liste de **personnes** ou de **groupes** .
- Par défaut, si une **personne** n'a pas de `allowlist`, on considère qu'elle peut tirer tout le monde.
- L'ensemble des **personnes** qu'une **personne** peut tirer est définie comme l'ensemble des gens contenus dans sa `allowlist` (ou voir règle précédente) moins l'ensemble des gens contenus dans sa `denylist`.

Voir le [fichier donné en exemple](examples/people.yaml) pour un exemple complexe d'architecture de groupes et de personnes.

#### 📧 Le fichier de configuration mail

Le fichier de configuration de mail est un fichier au format YAML. Il est passé avec l'argument `--auth`. Il est structuré comme suit:

```yaml
smtp:
  hostname: ...
  port: ... # optionnel, 587 par défaut
imap: # optionnel, utilise les mêmes paramètres que smtp par défaut
  hostname: ... # optionnel, `smtp.hostname` par défaut
  port: ... # optionnel, 143 par défaut
  sent_folder: ... # optionnel "Sent" par défaut
username: ...
password: ... # optionnel, demandé si non fourni
sender_mail: ... # optionnel, `username` par défaut
sender_name: ... # optionnel, `username` par défaut
```

Un fichier minimal ressemble à :

```yaml
smtp:
  hostname: "my_mail_server.org"
username: "my_mail@domain.ext"
```

Un fichier plus détaillé est [donné en exemple](examples/mail.yaml).

**Attention**, ce programme se connecte au serveur mail en *STARTTLS*. Ce protocole n'est pas supporté par tous les serveurs.

Par défaut, lorsqu'un tirage est effectué, les personnes reçoivent un mail de la part de l'adresse expéditrice et ces mails sont copiés dans la boîte d'envoi. Il est possible de désactiver la copie en passant en argument `--no-imap`.

#### 💬 Le fichier type de message

Ce fichier est obligatoirement utilisé pour l'envoi des courriels. Il est passé en argument avec `--message`. C'est un modèle ou patron de conception (*template*) dont certains champs vont être remplacés par les informations concernant cellui qui offre et cellui qui reçoit.

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
| `{sender_mail}` | Adresse mail expéditrice |
| `{sender_name}` | Nom associé à l'adresse expéditrice |
| `{gifter_id}` | Identifiant de la personne qui reçoit le courriel |
| `{gifter_name}` | Nom de la personne qui reçoit le courriel |
| `{gifter_nickname}` | Surnom de la personne qui reçoit le message |
| `{gifter_email}` | Adresse mail de la personne qui reçoit le courriel |
| `{giftee_id}` | Identifiant de la personne tirée au sort |
| `{giftee_name}` | Nom de la personne tirée au sort |
| `{giftee_nickname}` | Surnom de la personne qui reçoit le message |
| `{giftee_email}` | Adresse mail de la personne tirée au sort |

En pratique, seuls les champs `gifter_name`, `gifter_nickname`, `giftee_name` et `giftee_nickname` sont utiles, mais le reste est disponible si besoin.

Si ce fichier est passé en option lors du test de l'envoi des courriels (avec `--test-mail`), un mail est envoyé à l'adresse d'envoi avec des valeurs de test pour les champs à remplacer.

Il est possible de forcer le format d'envoi en passant `--text-format <value>` en argument. `<value>` peut être `txt`, `html` ou `auto`, par défaut `auto` qui essaie de déduire le format de l'extension.

## 🥳 Exemples d'utilisation

Effectuer un tirage avec les données fournies en exemple avec la graine aléatoire `jaaj42`, les exporter dans un fichier `tirage.txt` qui existait déjà et afficher ce tirage dans la console :

```sh
$ ronde -p examples/people.yaml -o tirage.txt --force -s --seed jaaj42
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

Tester la connection au serveur mail avec un message type et en forçant le format texte brut malgré l'extension :

```sh
$ ronde --test-mail -a examples/mail.yaml -m examples/message.html --text-format=txt
```

(Noter que dans ce cas les balises html seraient envoyées telles quelles, ce qui serait assez disgracieux.)

## 🔎 FAQ

> Pourquoi j'utiliserais un outil chelou en ligne de commande comme ça plutôt qu'un site tout fait qui s'occupe de tout ?

Bonne question, voilà des pistes de réflexions en vrac :

- Tu ne donnes pas tes données personnelles ni celles de tes proches à un tiers dont tu en ignores l'usage...
- Les sites ne gèrent pas (tous) un système de contrainte comme celui proposé qui permet de faire des tirages complexes, s'assurant par exemple que les couples ne se tirent pas entre eux, que les enfant ne puissent pas tirés d'adultes de la famille trop éloignée, tout ça.
- C'est stylé la ligne de commande en vrai, non ?
- Vive le logiciel libre !

> C'est un peu une usine à gaz ton truc. Moi j'ai juste un groupe de potes sans contraintes particulières.

Le format CSV est parfait pour ce genre de cas ;)

> Je veux faire un tirage pour ma famille de manière à ce que les adultes se tirent entre eux et les enfants entre eux, comment je fais ?

Cet outil génère un cycle hamiltonien, c'est à dire une boucle unique qui passe par toutes les personnes impliquées. Dans le cas proposé là, l'outil ne trouvera aucune solution, et affichera un message d'erreur. En effet la solution serait d'avoir deux cycles, un pour les adultes et un pour les enfants. Dans ce cas, il faudra faire deux tirages. Plus généralement, si il y a *N* sous-groupes qui n'interagissent pas les uns avec les autres, il faudra faire *N* tirages.

La possibilité de permettre à l'outil de générer le nombre minimal de cycles hamiltoniens est en cours de réflexion, mais c'est un problème difficile qui n'a peut être pas énormément de cas d'usage réels.

## 🤓 Comment contribuer ou aider ?

Déjà il n'y a pas besoin de savoir développer pour contribuer : tous les retours sont les bienvenus, que ce soient les problèmes ou les idées d'améliorations. Pour faire un retour, contacte-moi par mail ou mieux, si tu as un compte framagit, [crée un ticket](https://framagit.org/gabuzome/ronde-de-cadeaux/-/issues/new).

Si tu veux absolument développer et que tu utilises [Visual Studio Code](https://code.visualstudio.com/) (ou mieux [VSCodium](https://vscodium.com/)), un `.vscode/` existe pour simplifier le lancement des tests ou le debug. Si tu fais des merge requests, n'hésite pas à créer des tests unitaires pour t'assurer que tout fonctionne. Et il te faudra lancer tous les autres tests unitaires pour s'assurer de n'avoir rien cassé :

```sh
python -m unittest discover -s tests
```

Des pistes de trucs en vrac qui pourraient être chouette :

- Résoudre le problème de la couverture minimale du graphe par des cycles hamiltoniens.
- Traduire le projet dans plus de langues
- Faire de la GUI

Si vraiment tu as envie de donner de la bonne THUNE pour ce projet, déjà incroyable et merci, mais je n'en n'ai pas besoin donc donne plutôt aux associations qui œuvrent pour des causes justes, au hasard la [LPO 🐦](https://www.lpo.fr/), [La Quadrature du Net 🥧](https://www.laquadrature.net/), [Amnesty International 🕯️](https://www.amnesty.org/) ou l'[Association France Palestine Solidarité 🍉](https://www.france-palestine.org/)...

---

Ce projet est la continuation du projet ronde-de-cadeaux originel [disponible ici](https://framagit.org/bertille-ddp/ronde-de-cadeaux).