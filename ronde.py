"""

@author: Bertille Dubosq De Pesquidoux, Adrian "Relex12" Bonnet

The purpose of this script is to determine a cycle of people which should
offer a present to the next one on the cycle and to inform them trough
an e-mail
"""



from yaml import safe_load
import random
from lib.graph_generation import graph_gen
from lib.hamiltonian_path import hamilton
from lib.mail_sender import send_mails

class ImpossibleToDrawError(Exception):
    """
    This error is raised when `nb_err` exceeds `LIMIT_ERR_MAX`.
    """

LIMIT_ERR_MAX = 10
"""
When too many errors occur during the drawing, it is considered impossible.
"""

if __name__ == '__main__':
    data = safe_load(open('data.yaml', 'r'))
    mail_auth = safe_load(open('mail_auth.yaml', 'r'))
    message = open('message.txt', 'r').read()

    graph = graph_gen(data)

    drawable = False
    nb_err = 0
    while not drawable:
        path = hamilton(graph, len(graph), random.choice(list(graph)), [])
        if path is None:
            nb_err += 1
            print("Erreur")
        else:
            drawable = True
        if nb_err > LIMIT_ERR_MAX:
            print("No circuit found, try dropping some constraints.")
            raise ImpossibleToDrawError

    with open('circuit.txt', 'w') as f:
        # on sauvegarde le circuit obtenu dans un fichier au cas où ça planterait
        # quelque part au milieu de l'envoi de mails, pour ne pas se retrouver avec
        # un tirage incomplet
        f.write(str(path))

    send_mails(data["people"], path, mail_auth, message)
