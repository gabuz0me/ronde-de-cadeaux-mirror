# Ronde de cadeaux

**Ronde de cadeaux** est un outil libre pour tirer au sort des gens à qui faire des cadeaux façon *Secret Santa*, envoyant des mails aux participant⋅e⋅s pour leur indiquer la personne à régaler. Le tirage peut également être contrôlé par un mécanisme de listes de rejet ou de *cluster* pour ajouter des contraintes (par exemple on peut vouloir que des personnes en couple ne puissent pas tomber l'une sur l'autre).

---

## Comment qu'on s'en sert ?

### Installation du projet

Avec `git` clonez le repo, ou bien téléchargez ce projet sur votre ordinateur. Assurez-vous d'avoir Python 3 d'installé sur votre machine.

### Installation des dépendances

Ce projet python s'appuie sur les dépendances suivantes : `pyyaml`.  
Elle peut être installée avec `pip` (éventuellement dans un [environnement virtuel](https://docs.python.org/fr/3/library/venv.html)) avec :

```sh
pip install pyyaml
```

Ou bien directement via le fichier `requirements.txt` via:

```sh
pip install -r requirements.txt
```

### Utilisation

Voir déjà le message d'aide :

```console
$ ./ronde.py --help
Utilisation : ronde.py [-h] [-s] [-a AUTH] [-m MESSAGE] [-o OUTPUT] FICHIER

Ce programme permet de générer un tirage de gens à qui offrir des cadeaux en
prenant en compte un système de contraintes complexes. Si un chemin
hamiltonien est trouvé, un mail est envoyé à chacun⋅e des participant⋅e⋅s leur
indiquant à qui offrir un présent.

Arguments positionnels:
  FICHIER               Fichier yaml des données d'entrer à parser

Arguments optionnels:
  -h, --help            Afficher ce message et quitter
  -s, --show            Afficher la ronde calculée
  -a AUTH, --auth AUTH  Fichier de configuration mail
  -n, --no-imap         Ne pas copier les mails dans la boîte d'envoi
  -m MESSAGE, --message MESSAGE
                        Fichier mail type (Par défaut : .../message.txt)
  -o OUTPUT, --output OUTPUT
                        Fichier dans lequel exporter le tirage
```

1. Créer un fichier yaml avec dedans les données personnelles de vos ami⋅e⋅s. Possibilité de copier et adapter [`examples/example_data.yaml`](examples/example_data.yaml).
2. Afficher, exporter dans un fichier ou envoyer par mail le tirage.
  - Pour envoyer des mails, créer un fichier yaml avec les informations de connexion (voir [`examples/example_mail_auth.yaml`](examples/example_mail_auth.yaml) pour la structure) et le passer en argument `--auth`. Il faut dans ce cas que `message.txt` existe ou passer en argument `--message` un fichier texte faisant office de patron pour le mail. Les remplacement textuels suivant auront lieu:
    - `{sender_mail}` → adresse mail expéditrice,
    - `{sender_name}` → nom associé à l'adresse expéditrice,
    - `{gifter_mail}` → adresse de la personne qui reçoit le mail,
    - `{gifter_name}` et `{gifter_nickname}` → nom et surnom de la personne qui reçoit le message,
    - `{giftee_name}` et `{giftee_nickname}` → nom et surnom de la personne tirée.

    **Attention**, ce programme se connecte au serveur mail en STARTTLS. Ce n'est pas supporté par tous les serveurs.

  - Pour afficher la ronde calculée, passer `--show` en argument.
  - Pour sauvegarder le tirage dans un fichier, passer le nom du fichier en argument `--output`.
  - Il est possible de n'utiliser ni `--auth` ni `--show` ni `--output` : si le tirage se produit sans problème le programme n'affichera rien. Cela peut par exemple servir à tester si une solution est possible pour la configuration donnée.
3. Croiser les doigts.

Par exemple :

```console
$ ./ronde.py examples/example_data.yaml --show
               Nick Qux → Alice-Andréa-Alexia Foo
Alice-Andréa-Alexia Foo → Gulliver Bar
           Gulliver Bar → Bœbælius Foo
           Bœbælius Foo → Flora Bar
              Flora Bar → Linda Qux
              Linda Qux → Henry Bar
              Henry Bar → Dave Foo
               Dave Foo → Isöbel Bar
             Isöbel Bar → Cärol Foo
              Cärol Foo → Eve Bar
                Eve Bar → Mark Qux
               Mark Qux → Jack Baz
               Jack Baz → Nick Qux
```

## FAQ

> Pourquoi j'utiliserais un outil chelou en ligne de commande comme ça plutôt qu'un site tout fait qui s'occupe de tout ?

Bonne question, voilà des pistes de réflexions en vrac :

- Tu ne donnes pas tes données personnelles ni celles de tes proches à un tiers dont tu en ignores l'usage...
- Les sites ne gèrent pas (tous) un système de contrainte comme celui proposé qui permet de faire des tirages complexes, s'assurant par exemple que les couples ne se tirent pas entre eux, que les enfant ne puissent pas tirés d'adultes de la famille trop éloignée, tout ça.
- C'est stylé la ligne de commande en vrai, non ?
- Vive le logiciel libre !

> C'est un peu une usine à gaz ton truc. Moi j'ai juste un groupe de potes sans contraintes particulières.

Il suffit juste de ne pas déclarer de *clusters* et de ne pas mettre d'*allowlist* ou de *denylist* !

> Ah en fait maintenant que j'y pense il y a deux personnes qui peuvent pas se blairer…

C'est possible de juste les interdire mutuellement, soit en créant un cluster les contenant soit en ajoutant pour chacun⋅e le nom de l'autre dans leur `denylist`.

> Je veux faire un tirage pour ma famille et que les adultes se tirent entre eux et les enfants entre eux, comment je fais ?

Cet outil génère un cycle hamiltonien, c'est à dire une boucle unique qui passe par toutes les personnes impliquées. Dans le cas proposé là, l'outil ne trouvera aucune solution, en effet une solution serait une boucle d'adultes et une autre boucle, pour les enfants. Dans ce cas, il faudra faire deux tirages. Plus généralement, si il y a *N* sous-groupes qui n'intéragissent pas les uns avec les autres, il faudra faire *N* tirages.

> Oué alors moi j'avais fait tout un fichier de config l'année dernière, un truc bien quali tavu, et cette année ça marche même plus vazy j'me désabonne.

La structure de donnée a changé en décembre 2023. Mais tu peux utiliser [le convertisseur](tools/data_converter_2023_12_08.py) pour transformer tes anciennes données dans le nouveau format !

> On peut contribuer ?

OUI. Pour des idées de contributions, voir la section suivante.

## Comment contribuer ?

Déjà il n'y a pas besoin d'être dev pour contribuer : tous les retours sont les bienvenus, que ce soient les problèmes ou les idées d'améliorations. Pour faire un retour, contactez-nous par mail ou mieux, si vous avez un compte framagit, [créez un ticket](https://framagit.org/bertille-ddp/ronde-de-cadeaux/-/issues/new).

Si vous faites une merge request, n'hésitez pas à créer des tests unitaires pour vous assurer que tout fonctionne. Et il faudra lancer tous les autres tests unitaires pour s'assurer de n'avoir rien cassé :

```sh
python -m unittest tests/test_xxx.py
```

Et sinon des pistes de trucs en vrac :

- [ ] Au moment de construire le graphe, la liste d'autorisation est d'abord évaluée, et ensuite les gens de la liste d'interdiction sont enlevés. On pourrait imaginer le contraire, un comportement où les gens sur liste d'autorisation sont **forcément** autorisés.
- [ ] Si plusieurs groupes sont sur liste d'autorisation (resp. d'interdiction), tous les membres de tous les groupes sont inclus (resp. exclus). C'est un OU logique. On pourrait imaginer de laisser le choix à l'utilisateur·ice de faire un OU ou un ET.
- [ ] De façon plus générale, on pourrait faire quelque chose de plus interactif. En particulier, quand aucune solution n'est trouvée, on pourrait proposer d'abandonner certaines contraintes et de réessayer (la liste d'autorisation, la liste d'interdiction ou le circuit hamiltonien (mais ça ce serait plus relou à implémenter)).
- [ ] Faire de la GUI, [WIP ici](https://framagit.org/gabuzome/guirlande-de-cadeaux/) :D

## Motivations

Le but de cet outil est d'attribuer à chaque personne d'un groupe une autre personne à qui faire un cadeau, tout en respectant certaines contraintes. En effet, j'ai bricolé quelque chose qui s'adapte à mon contexte familial. En particulier :

- Pour forcer un peu de mélange, on ne veut pas que des conjoint·es puissent se piocher entre elleux. Des adelphes non plus. Ça veut dire mettre en place un système de liste d'interdiction.
- Les parents font déjà des cadeaux à leurs enfants hors de la ronde. On ne veut donc pas qu'iels les tirent, pour éviter la redondance. Ça veut dire que le graphe de qui peut tirer qui est orienté.
- On veut que les plus jeunes ne puissent tirer que des gens de leur génération, pour qui iels trouveront plus facilement des idées de cadeau. Ça veut dire mettre en place un système de liste d'autorisation. (Pas réciproque non plus : on peut être de la plus jeune génération mais avoir plus de 15 ans)
- On est nombreuxes. Écrire pour chacun·e une liste des personnes autorisées ou interdites, c'est pas gérable. Ça veut dire avoir un mécanisme où on définit des groupes (qui peuvent être des unions de groupes) à un endroit, qui sont réutilisés pour les listes d'interdiction et d'autorisation.

Le système final est assez souple. On peut imaginer par exemple un cas d'usage en entreprise :

- Par défaut, on ne doit pas pouvoir piocher quelqu'un·e de son service, pour forcer le mélange.
- Les stagiaires, qui sont moins bien intégré·es, peuvent piocher quelqu'un·e de leur service ou bien un·e autre stagiaire.

Il suffit de déclarer la composition de chaque service et la liste des stagiaires et puis hop, deny ou allowlister correctement pour chaque personne et le tour est joué.

Dans les autres features, il y a quelques garde-fous pour éviter certaines erreurs d'interface chaise-clavier :

- En utilisant une première fois Secret-Santa, j'avais oublié de mettre chaque personne dans sa propre denylist et quelqu'une s'était tirée elle-même. Là, au moment de la génération du graphe des tirages potentiels, cette possibilité est bien éliminée.
- En le relançant pour corriger cette erreur, j'avais mal saisi une adresse mail. Pas moyen ensuite de retrouver l'information de qui avait été tiré et, sans pouvoir redonner l'instruction manuellement, il a fallu faire un troisième tirage. Ça commence à faire beaucoup de confusion (et de la mauvaise pub pour les outils libres). Du coup, entre le tirage au sort et l'envoi des mails, les attributions sont écrites dans un fichier txt pour pouvoir être retrouvées au cas où. Et puis les mails envoyés sont copiés dans le dossier des mails sortants. Ceinture + bretelles.

Enfin, pour toujours plus d'inclusion et de fun au moment de l'ouverture, on veut faire une seule grande chaîne avec tout le monde. Ce qui, en termes compréhensibles par quelqu'un·e qui lit un README, veut dire qu'il nous faut un algorithme pour trouver un circuit hamiltonien.

---

Ce projet s'inspire notamment de l'outil de tirage Secret-Santa, développé par Adrian "Relex12" Bonnet sous licence MIT et que l'on peut retrouver ici : [https://github.com/Relex12/Secret-Santa](https://github.com/Relex12/Secret-Santa)

Contributeurices :
- Bertille Dubosc de Pesquidoux
- Adrien Laporte
- Adrian "Relex12" Bonnet
- Vincent Menegaux