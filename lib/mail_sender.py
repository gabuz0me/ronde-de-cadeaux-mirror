from typing import Dict, List
import smtplib
import imaplib
import time

def send_mails(people: Dict, path: List, mail_auth: Dict, message: str):
    try:
        # connexion au serveur SMTP pour l'envoi de mail
        smtp_server = smtplib.SMTP(host=mail_auth['hostname'], port=mail_auth['smtp_port'])
        smtp_server.starttls()
        smtp_server.login(mail_auth['username'], mail_auth['password'])

        # connexion au serveur IMAP pour copier le message envoyé
        # (et pouvoir le renvoyer manuellement en cas de pépin)
        imap_server = imaplib.IMAP4(mail_auth['hostname'], mail_auth['imap_port'])
        imap_server.starttls()
        imap_server.login(mail_auth['username'], mail_auth['password'])

        for person in people:
            # logiquement la personne doit faire un cadeau à cellui qui la suit dans la liste
            giftee_name = path[(path.index(person["name"])+1)%len(path)]

            # on remplace les variables par leurs valeurs
            msg = message.format(mail_auth['sender'], person["email"], person["name"], giftee_name).encode('utf-8')
            
            # et on envoie
            # print (f"{person['name']} doit donner un cadeau à {giftee_name}")
            smtp_server.sendmail(mail_auth['sender'], person["email"], msg)
            imap_server.append(mail_auth['sent_folder'], '\\Seen', imaplib.Time2Internaldate(time.time()), msg)

        imap_server.logout()
        smtp_server.close()

        print ("L'envoi de mail a réussi")

    except Exception as e:
        print ("Erreur : "+str(e))
