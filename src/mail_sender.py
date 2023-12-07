import imaplib
import smtplib
import time
from typing import Dict, List
from .graph_generation import Person

class Default(dict):
    """Laisser inchanger les clés non trouvées dans le formattage de String"""
    def __missing__(self, key): 
        return key.join("{}")
    
def format_message_mail(sender_mail:str, sender_name: str, template_message: str) -> str:
    # on remplace les variables par leurs valeurs
    msg = template_message.format_map(Default({
        'sender_mail':sender_mail,
        'sender_name':sender_name,
    }))
    return msg

def format_message_people(gifter: Person, giftee: Person, template_message: str) -> str:
    msg = template_message.format_map(Default({
        'gifter_name'    :gifter.name,
        'gifter_nickname':gifter.nickname,
        'gifter_mail'    :gifter.email,
        'giftee_name'    :giftee.name,
        'giftee_nickname':giftee.nickname,
    }))
    return msg


def send_mails(people_object_dict: Dict, gifter_giftee_tuple: List, mail_auth: Dict, template_message: str):
    copy_to_sent_folder = mail_auth['copy_to_sent_folder']

    smtp_server = None
    imap_server = None

    smtp_hostname = ''
    try :
        smtp_hostname = mail_auth['smtp_hostname']
        # connexion au serveur SMTP pour l'envoi de mail
        smtp_server = smtplib.SMTP(
            host=smtp_hostname,
            port=mail_auth['smtp_port'],
        )
        smtp_server.starttls()
        smtp_server.login(
            mail_auth['username'],
            mail_auth['password'],
        )
    except:
        print("Impossible de se connecter au serveur SMTP")
        exit()

    if copy_to_sent_folder:
        try:
            # connexion au serveur IMAP pour copier le message envoyé
            # (et pouvoir le renvoyer manuellement en cas de pépin)
            imap_server = imaplib.IMAP4(
                mail_auth.get('imap_hostname', smtp_hostname),
                mail_auth['imap_port'],
            )
            imap_server.starttls()
            imap_server.login(
                mail_auth['username'],
                mail_auth['password'],
            )
        except:
            print("Impossible de se connecter au serveur IMAP")
            smtp_server.close()
            exit()

    # C'est parti pour l'envoi !
    try:
        sender_mail = mail_auth['sender_mail']
        msg_base = format_message_mail(sender_mail, mail_auth['sender_name'], template_message)

        for gifter, giftee in gifter_giftee_tuple:
            gifter = people_object_dict[gifter]
            giftee = people_object_dict[giftee]
            msg = format_message_people(gifter, giftee, msg_base)
            msg = msg.encode('utf-8')

            # print(f"{gifter.name} doit donner un cadeau à {giftee.name}")
            smtp_server.sendmail(sender_mail, gifter.email, msg)
            if copy_to_sent_folder:
                imap_server.append(
                    mailbox=mail_auth['sent_folder'],
                    flags='\\Seen',
                    date_time=imaplib.Time2Internaldate(time.time()),
                    message=msg,
                )

    except Exception as e:
        print(f"Erreur : {repr(e)}")

    else:
        print("L'envoi de mail a réussi")

    finally:
        if imap_server is not None : imap_server.logout()
        smtp_server.close()

