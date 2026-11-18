<div align=center>

# Ronde de Cadeaux

❖ [Français](https://framagit.org/gabuzome/ronde-de-cadeaux/-/blob/main/README.md) ❖ **English** ❖

</div>

---

**Ronde de Cadeaux** is an open-source command line interface tool to create *Secret Santa* events where participants are notified by email. The draw can be controlled using constraints, like for instance preventing a person to be assigned a specific person or making sure they can only gift to people in a given group.

<!--[[[cog
import os,sys; os.environ["COLUMNS"]="100"; assert sys.version_info>=(3,14), "cog Python>=3.14"
from ronde_de_cadeaux import main; os.environ["RONDE_LANG"]="en"
print("```");main(["--help"]);print("```")
]]]-->
```
usage: ronde [-h] [--version] [-v | -q] [--test-email] [-a AUTH] [-m MESSAGE] [-p PEOPLE] [-s]
             [-o OUTPUT] [--force] [--seed SEED]

This program generates random draws for secret gifting cycles, allowing complex constraints

options:
  -h, --help             show this help message and exit
  --version              show program version and exit
  -v, --verbose          verbose mode
  -q, --quiet            quiet mode
  --test-email           test email server configuration
  -a, --auth AUTH        mail server configuration file, see the documentation for the schema
  -m, --message MESSAGE  template message for the email, see the documentation for the schema
  -p, --people PEOPLE    people configuration file, (YAML or CSV, see the documentation for the
                         schema)
  -s, --show             show the computed cycle
  -o, --output OUTPUT    output file to export the draw
  --force                overwrite the output file if it already exists
  --seed SEED            random seed for the draw
```
<!--[[[end]]] (sum: nUGHib2Yah)-->