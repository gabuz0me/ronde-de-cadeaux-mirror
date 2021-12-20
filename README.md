# Ronde de cadeaux
Un outil pour tirer au sort des gens à qui faire des cadeaux.

Ce projet s'inspire notamment de l'outil de tirage Secret-Santa, développé par Adrian "Relex12" Bonnet sous licence MIT et que l'on peut retrouver ici : https://github.com/Relex12/Secret-Santa


## Motivations
Le but de cet outil est d'attribuer à chaque personne d'un groupe une autre personne à qui faire un cadeau, tout en respectant certaines contraintes. En effet, j'ai bricolé quelque chose qui s'adapte à mon contexte familial. En particulier :
- Pour forcer un peu de mélange, on ne veut pas que des conjoint·es puissent se piocher entre elleux. Des adelphes non plus. Ça veut dire mettre en place un système de liste noire.
- Les parents font déjà des cadeaux à leurs enfants hors de la ronde. On ne veut donc pas qu'iels les tirent, pour éviter la redondance. Ça veut dire que le graphe de qui peut tirer qui est orienté.
- On veut que les plus jeunes ne puissent tirer que des gens de leur génération, pour qui iels trouveront plus facilement des idées de cadeau. Ça veut dire mettre en place un système de liste blanche. (Pas réciproque non plus : on peut être de la plus jeune génération mais avoir plus de 15 ans)
- On est nombreuxes. Écrire pour chacun·e une liste des personnes autorisées ou interdites, c'est pas gérable. Ça veut dire avoir un mécanisme où on définit des groupes (qui peuvent être des unions de groupes) à un endroit, qui sont réutilisés pour les listes noire et blanche.

Le système final est assez souple. On peut imaginer par exemple un cas d'usage en entreprise :
- Par défaut, on ne doit pas pouvoir piocher quelqu'un·e de son service, pour forcer le mélange.
- Les stagiaires, qui sont moins bien intégré·es, peuvent piocher quelqu'un·e de leur service ou bien un·e autre stagiaire.

Il suffit de déclarer la composition de chaque service et la liste des stagiaires et puis hop, black ou whitelister correctement pour chaque personne et le tour est joué.

Dans les autres features, il y a quelques garde-fous pour éviter certaines erreurs d'interface chaise-clavier :
- En utilisant une première fois Secret-Santa, j'avais oublié de mettre chaque personne dans sa propre blacklist et quelqu'une s'était tirée elle-même. Là, au moment de la génération du graphe des tirages potentiels, cette possibilité est bien éliminée.
- En le relançant pour corriger cette erreur, j'avais mal saisi une adresse mail. Pas moyen ensuite de retrouver l'information de qui avait été tiré et, sans pouvoir redonner l'instruction manuellement, il a fallu faire un troisième tirage. Ça commence à faire beaucoup de confusion (et de la mauvaise pub pour les outils libres). Du coup, entre le tirage au sort et l'envoi des mails, les attributions sont écrites dans un fichier txt pour pouvoir être retrouvées au cas où. Et puis les mails envoyés sont copiés dans le dossier des mails sortants. Ceinture + bretelles.

Enfin, pour toujours plus d'inclusion et de fun au moment de l'ouverture, on veut faire une seule grande chaîne avec tout le monde. Ce qui, en termes compréhensibles par quelqu'un·e qui lit un README, veut dire qu'il nous faut un algorithme pour trouver un circuit hamiltonien.


## Comment qu'on s'en sert ?
1. Créer un fichier `data.yaml` avec dedans les données personnelles de vos ami·es. Possibilité de copier et adapter celui contenu dans `examples`.
2. Idem pour `mail_auth.yaml`.
3. Adapter `message.txt`, sachant que `{0}` sera remplacé par votre adresse mail, `{1}` par l'adresse de la personne qui reçoit le mail, `{2}` par son nom et `{3}` par le nom de la personne tirée.
4. `python ronde.py`
5. Croiser les doigts.


## FAQ
> C'est un peu une usine à gaz ton truc. Moi j'ai juste un groupe de potes sans contraintes particulières.

Il suffit juste de ne pas déclarer de clusters et de ne pas mettre de whitelist ou blacklist !

> Ah en fait maintenat que j'y pense il y a deux personnes qui peuvent pas se blairer…

C'est possible de juste les interdire mutuellement ! Si `data.yaml` ne contient pas de section `clusters` mais que certaines personnes ont un attribut `blacklist` (ou `whitelist`), alors il est interprété comme une liste de personnes à blacklister.

> On peut contribuer ?

OUI. Pour des idées de contributions, voir la section suivante.


## Défauts / pistes d'amélioration
- [ ] C'est fait globalement à l'arrache et dans l'urgence alors il y a sans doute pas mal de trucs stupides. Aussi, je connais pas très bien le Python, ses bonnes pratiques, les PEPs, ce qui est plus ou moins idiomatique, comment gérer proprement des exceptions…
- [ ] La construction du graphe des tirages possibles est pas très élégante, on pourrait certainement faire moins de boucles for.
- [ ] Pareil, niveau complexité, c'est sans doute pas OP, on pourrait trouver de meilleurs algorithmes (ou utiliser des libs faites pour manipuler des graphes).
- [ ] Le formattage de string pour le message est sale.
- [ ] Il n'y a pas de vérification de l'unicité des personnes (et j'ai pas testé ce qui se passe en cas d'homonymes).
- [ ] La construction de listes de listes n'a aucune protection contre les boucles infinies. Aussi, il faut faire attention à l'ordre dans lequel on les déclare. (Dans l'exemple, chacune des listes `siblings` est déclarée avant la liste `cousins`, qui est l'union des deux. Le comportement quand c'est pas le cas n'est pas testé.)
- [ ] Il n'est pas possible de faire cohabiter les deux mécanismes de blacklist (une personne qui ne pourrait tirer ni George ni Alfred, et une autre qui ne pourrait pas tirer les Amants de Venise ; c'est pour tout le fichier soit des gens soit des groupes).
- [ ] Au moment de construire le graphe, la liste blanche est d'abord évaluée, et ensuite les gens de la liste noire sont enlevés. On pourrait imaginer le contraire, un comportement où les gens sur liste blanche sont **forcément** autorisés.
- [ ] Si plusieurs groupes sont sur liste blanche (resp. noire), tous les membres de tous les groupes sont inclus (resp. exclus). C'est un OU logique. On pourrait imaginer de laisser le choix à l'utilisateur·ice de faire un OU ou un ET.
- [ ] De façon plus générale, on pourrait faire quelque chose de plus interactif. En particulier, quand aucune solution n'est trouvée, on pourrait proposer d'abandonner certaines contraintes et de réessayer (la liste blanche, la liste noire ou le circuit hamiltonien (mais ça ce serait plus relou à implémenter)).
- [ ] Pouvoir afficher de l'aide et passer des options pour contrôler plus finement le comportement.
- [ ] Demander le mot de passe de la boîte mail au moment de l'exécution pour ne pas le laisser se balader dans la nature.
