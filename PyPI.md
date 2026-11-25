<div align=center>

# Ronde de Cadeaux

❖ [Français](https://framagit.org/gabuzome/ronde-de-cadeaux/-/blob/main/README.md) ❖ [English](https://framagit.org/gabuzome/ronde-de-cadeaux/-/blob/main/README-en.md) ❖


#### ➡️ [Documentation](https://framagit.org/gabuzome/ronde-de-cadeaux/) ⬅️

</div>

---

<div align="center">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/English_language.svg/500px-English_language.svg.png" height="30" alt="EN"/>
</div>

**Ronde de Cadeaux** is an open-source command line interface tool to create *Secret Santa* events where participants are notified by email. The draw can be controlled using constraints, like for instance preventing a person to be assigned a specific person or making sure they can only gift to people in a given group.

<!--[[[cog
import os; os.environ["COLUMNS"]="100";os.environ["NO_COLOR"]="1";
from ronde_de_cadeaux import main; os.environ["RONDE_LANG"]="en"
print("```");main(["--help"]);print("```")
]]]-->
```
Usage: ronde [-h] [--version] [-v | -q] [--test-email] [-e FILE] [-m FILE] [-p FILE] [-s]
             [-o FILE] [--overwrite] [--seed SEED]

This program generates random draws for secret gifting cycles, allowing complex constraints.

These draws can be shown, exported or sent by email to the participants.

Options:
  -h, --help               Show this help message and exit
  --version                Show program version and exit
  -v, --verbose            Verbose mode
  -q, --quiet              Quiet mode
  --test-email             Send a test email using the sending address to check the email server
                           configuration
  -e, --email-config FILE  Email server configuration file, see the documentation for the schema
  -m, --message FILE       Template message file for the email (HTML or text, see the
                           documentation for the formatting)
  -p, --people FILE        People configuration file (YAML or CSV, see the documentation for the
                           schema)
  -s, --show               Show the computed cycle
  -o, --output FILE        Output file to export the draw
  --overwrite              Overwrite the output file if it already exists
  --seed SEED              Random seed for the draw

The option --email-config requires a template message file to be passed using --message.

If --test-email is passed, --email-config must be passed too. A template message file can also be
passed to check final email formatting.

When not testing the email server configuration, a people configuration file must be passed using
--people, and at least one of the three following actions must be done among showing the draw
(--show), writing it to a file (--output) or sending it by email (--email-config).

For more information, see the documentation.
```
<!--[[[end]]] (sum: fn5iuF1fF8)-->

---

<div align="center">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Flag_of_French_language.svg/500px-Flag_of_French_language.svg.png" height="30" alt="FR"/>
</div>

**Ronde de Cadeaux** est un outil libre en ligne de commande pour tirer au sort des gens à qui faire des cadeaux façon *Secret Santa* ou *Noël Canadien*, envoyant des courriels aux participant⋅e⋅s pour leur indiquer la personne à régaler. Le tirage peut également être contrôlé par différents mécanismes de contraintes, comme par exemple empêcher une personne de tirer une personne spécifique ou faire en sorte qu'elle en tire une dans un groupe donné.

<!--[[[cog
import os; os.environ["COLUMNS"]="100";os.environ["NO_COLOR"]="1";
from ronde_de_cadeaux import main; os.environ["RONDE_LANG"]="fr"
print("```");main(["--help"]);print("```")
]]]-->
```
Utilisation : ronde [-h] [--version] [-v | -q] [--test-email] [-e FICHIER] [-m FICHIER]
                    [-p FICHIER] [-s] [-o FICHIER] [--overwrite] [--seed GRAINE]

Ce programme permet de générer un tirage de gens à qui offrir des cadeaux en prenant en compte un
système de contraintes complexes.

Ces tirages peuvent ensuite être affichés, exportés ou envoyés par courriel.

Options :
  -h, --help                  Affiche ce message et termine le programme
  --version                   Affiche le numéro de version et termine le programme
  -v, --verbose               Active le mode verbeux
  -q, --quiet                 Réduit les messages affichés
  --test-email                Envoie un courriel de test via l'adresse expéditrice pour vérifier
                              la configuration du serveur de messagerie
  -e, --email-config FICHIER  Fichier de configuration du serveur de messagerie pour l'envoi des
                              courriels, voir la documentation pour le schéma
  -m, --message FICHIER       Fichier de gabarit du message envoyé par courriel (HTML ou texte,
                              voir la documentation pour le formatage)
  -p, --people FICHIER        Fichier de configuration des personnes (YAML ou CSV, voir la
                              documentation pour le schéma)
  -s, --show                  Affiche la ronde calculée
  -o, --output FICHIER        Fichier dans lequel exporter le tirage
  --overwrite                 Force l'écriture dans le fichier de sortie, même si celui-ci existe
                              déjà
  --seed GRAINE               Graine aléatoire pour le tirage

L'option --email-config nécessite qu'un fichier de gabarit de message soit passé avec --message.

Si l'option --test-email est passée, il faut également passer --email-config. Un fichier de gabarit
de message peut être donné optionnellement avec --message pour s'assurer du rendu.

Quand la connexion au serveur de messagerie n'est pas testée, il faut nécessairement passer un
fichier de configuration des personnes avec --people ainsi qu'effectuer au moins une des trois
actions possibles parmi afficher (--show), exporter dans un fichier (--output) ou envoyer le tirage
par mail (--email-config).

Pour plus d'information, voir la documentation.
```
<!--[[[end]]] (sum: v1udOhbsOE)-->

---

<div align="center">

#### ➡️ [Documentation](https://framagit.org/gabuzome/ronde-de-cadeaux/) ⬅️

</div>