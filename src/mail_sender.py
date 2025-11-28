"""Module d'envoi de mails."""

import getpass
import imaplib
import smtplib
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any

from .graph_generation import Person
from .logger import logger


class _DefaultFormatter(dict):
    """Laisser inchangées les clés non trouvées dans le formatage de String."""

    def __missing__(self, key: str) -> str:
        return key.join("{}")


def format_message_people(gifter: Person, giftee: Person, template_message: str) -> str:
    """Remplace les champs utiles dans le template de message."""
    msg = template_message.format_map(
        _DefaultFormatter(
            {
                "gifter_name": gifter.name,
                "gifter_nickname": gifter.nickname,
                "gifter_mail": gifter.email,
                "giftee_name": giftee.name,
                "giftee_nickname": giftee.nickname,
            }
        )
    )
    return msg


class MailInfo:
    """Wrapper contenant toute les informations relatives à l'envoi de mail."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.hostname: str = data["hostname"]
        self.port_smtp: int = data.get("port_smtp", 587)
        self.hostname_imap: str | None = None
        self.port_imap: int | None = None
        self.sent_folder: str | None = None
        self.copy_to_sent_folder: bool = data["copy_to_sent_folder"]
        if self.copy_to_sent_folder:
            self.hostname_imap = data.get("hostname_imap", self.hostname)
            self.port_imap = data.get("port_imap", 143)
            self.sent_folder = data.get("sent_folder", "Sent")
        self.username: str = data["username"]
        self.password: str | None = data.get("password")
        if self.password is None:
            self.password = getpass.getpass("Mot de passe mail :")  # n'affiche pas ce qui est tapé
        self.sender_mail: str = data.get("sender_mail", self.username)
        self.sender_name: str = data.get("sender_name", self.username)
        self.message: str = data["message"]
        self.plain_text: bool = data["plain_text"]


def create_servers(mail_info: MailInfo) -> tuple[smtplib.SMTP, imaplib.IMAP4 | None]:
    """Crée les serveurs.

    S'il y a des erreurs, fait s'arrêter le programme et quitte.
    """
    try:
        smtp_server = smtplib.SMTP(
            host=mail_info.hostname,
            port=mail_info.port_smtp,
        )
        smtp_server.starttls()
        smtp_server.login(
            mail_info.username,
            mail_info.password,
        )
    except Exception as e:  # noqa
        logger.error("Impossible de se connecter au serveur SMTP")
        # print(e)
        exit(1)

    imap_server: imaplib.IMAP4 | None = None
    if mail_info.copy_to_sent_folder:
        try:
            imap_server = imaplib.IMAP4(
                mail_info.hostname_imap,
                mail_info.port_imap,
            )
            imap_server.starttls()
            imap_server.login(
                mail_info.username,
                mail_info.password,
            )
        except Exception as e:  # noqa
            logger.error("Impossible de se connecter au serveur IMAP")
            smtp_server.close()
            # print(e)
            exit(1)

    return smtp_server, imap_server


def message_to_subject_body(message: str) -> tuple[str, str]:
    """À partir d'un message, extrait l'objet et le corps de texte."""
    as_list = message.split("\n")
    subject = as_list[0]
    body = "".join(as_list[1:]).strip()

    return subject, body


def mail_data_to_mail_info(mail_data: dict[str, Any]) -> MailInfo:
    """Convertir un dictionnaire en `MailInfo`."""
    try:
        mail_info = MailInfo(mail_data)
    except Exception as e:  # noqa
        logger.error("Fichier de configuration mail invalide")
        # print(e)
        exit(1)
    return mail_info


def _to_header(msg: str) -> str:
    return str(Header(msg, "utf-8"))


def test_mail_sending(mail_info: MailInfo) -> None:
    """Tester la configuration mail."""
    smtp_server, imap_server = create_servers(mail_info)
    sender = formataddr((_to_header(mail_info.sender_name), mail_info.sender_mail))

    mail = MIMEMultipart()
    mail["From"] = sender
    mail["To"] = sender
    mail["Subject"] = _to_header("Test de configuration Ronde de Cadeaux")
    mail.attach(MIMEText("Ça a l'air de marcher :D"))

    try:
        smtp_server.sendmail(mail_info.sender_mail, mail_info.sender_mail, mail.as_string())
    except Exception as e:  # noqa
        logger.error("Erreur d'envoi SMTP")
        # print(e)
        exit(1)

    if mail_info.copy_to_sent_folder:
        try:
            imap_server.append(
                mailbox=mail_info.sent_folder,
                flags="\\Seen",
                date_time=imaplib.Time2Internaldate(time.time()),
                message=mail.as_bytes(),
            )
        except Exception as e:  # noqa
            logger.error("Erreur de copie IMAP")
            # print(e)
            exit(1)
    logger.info("Tout a l'air de fonctionner!")


def send_mails(gifter_giftee_tuple: list[tuple[Person, Person]], mail_info: MailInfo) -> None:
    """Envoi des mails!."""
    smtp_server, imap_server = create_servers(mail_info)
    try:
        sender = formataddr((_to_header(mail_info.sender_name), mail_info.sender_mail))

        for gifter, giftee in gifter_giftee_tuple:
            mail = MIMEMultipart()
            mail["From"] = sender
            mail["To"] = formataddr((_to_header(gifter.name), gifter.email))
            formatted = format_message_people(gifter, giftee, mail_info.message)
            subject, body = message_to_subject_body(formatted)
            mail["Subject"] = _to_header(subject)
            mail.attach(MIMEText(body, "plain" if mail_info.plain_text else "html"))

            smtp_server.sendmail(mail_info.sender_mail, gifter.email, mail.as_string())
            if mail_info.copy_to_sent_folder:
                imap_server.append(
                    mailbox=mail_info.sent_folder,
                    flags="\\Seen",
                    date_time=imaplib.Time2Internaldate(time.time()),
                    message=mail.as_bytes(),
                )

    except Exception as e:
        logger.error(f"Erreur : {repr(e)}")

    else:
        logger.info("L'envoi de mail a réussi.")

    finally:
        if imap_server is not None:
            imap_server.logout()
        smtp_server.close()
