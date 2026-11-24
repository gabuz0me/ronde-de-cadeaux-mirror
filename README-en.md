<div align=center>

# Ronde de Cadeaux

❖ [Français](https://framagit.org/gabuzome/ronde-de-cadeaux/-/blob/main/README.md) ❖ **English** ❖

</div>

---

**Ronde de Cadeaux** is an open-source command line interface tool to create *Secret Santa* events where participants are notified by email. The draw can be controlled using constraints, like for instance preventing a person to be assigned a specific person or making sure they can only gift to people in a given group.

<!--[[[cog
import os; os.environ["COLUMNS"]="100";os.environ["NO_COLOR"]="1";
from ronde_de_cadeaux import main; os.environ["RONDE_LANG"]="en"
print("```");main(["--help"]);print("```")
]]]-->
```
usage: ronde [-h] [--version] [-v | -q] [--test-email] [-e FILE] [-m FILE] [-p FILE] [-s]
             [-o FILE] [--overwrite] [--seed SEED]

This program generates random draws for secret gifting cycles, allowing complex constraints.

These draws can be shown, exported or sent by email to the participants.

options:
  -h, --help               show this help message and exit
  --version                show program version and exit
  -v, --verbose            verbose mode
  -q, --quiet              quiet mode
  --test-email             send a test email using the sending address to check the email server
                           configuration
  -e, --email-config FILE  email server configuration file, see the documentation for the schema
  -m, --message FILE       template message file for the email (HTML or text, see the
                           documentation for the formatting)
  -p, --people FILE        people configuration file (YAML or CSV, see the documentation for the
                           schema)
  -s, --show               show the computed cycle
  -o, --output FILE        output file to export the draw
  --overwrite              overwrite the output file if it already exists
  --seed SEED              random seed for the draw

The option --email-config requires a template message file to be passed using --message.

If --test-email is passed, --email-config must be passed too. A template message file can also be
passed to check final email formatting.

When not testing the email server configuration, a people configuration file must be passed using
--people, and at least one of the three following actions must be done among showing the draw
(--show), writing it to a file (--output) or sending it by email (--email-config).

For more information, see the documentation.
```
<!--[[[end]]] (sum: xaZMOik7U+)  -->