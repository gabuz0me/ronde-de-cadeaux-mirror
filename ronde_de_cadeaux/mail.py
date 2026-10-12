"""Module relatif au mails.

Validation des données et envoi.
"""

import getpass
import imaplib
import smtplib
import sys
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path
from typing import Any, ClassVar, NamedTuple, Self

import yaml
from pydantic import BaseModel, ValidationError

from .graph_generation import Draw, PersonLike, PersonTuple
from .logger import logger


class _DefaultFormatter(dict[str, Any]):
    """Laisser inchangées les clés non trouvées dans le formatage de String."""

    def __missing__(self, key: str) -> str:
        return key.join("{}")


def format_message_people(gifter: PersonLike, giftee: PersonLike, template_message: str) -> str:
    """Remplace les champs utiles dans le template de message."""
    msg = template_message.format_map(
        _DefaultFormatter(
            {
                "gifter_id": gifter.id,
                "gifter_name": gifter.name,
                "gifter_nickname": gifter.nickname,
                "gifter_mail": gifter.email,
                "giftee_id": giftee.id,
                "giftee_name": giftee.name,
                "giftee_nickname": giftee.nickname,
                "giftee_mail": giftee.email,
            }
        )
    )
    return msg


class _SMTPModel(BaseModel):
    hostname: str
    port: int = 587


class _IMAPModel(BaseModel):
    DefaultPort: ClassVar[int] = 143
    DefaultSentFolder: ClassVar[str] = "Sent"

    hostname: str | None = None
    port: int = DefaultPort
    sent_folder: str = DefaultSentFolder


class _MailModel(BaseModel):
    smtp: _SMTPModel
    imap: _IMAPModel | None = None
    username: str
    password: str | None = None
    sender_mail: str | None = None
    sender_name: str | None = None


class Message(NamedTuple):
    """Un message et son format."""

    text: str
    is_plain_text: bool

    @classmethod
    def FromMessagePath(cls, message_path: Path | None, text_format: str) -> Self | None:
        """Crée un message ou pas selon le chemin et le format précisé."""
        if message_path:
            with open(message_path, "r", encoding="utf-8") as f:
                message_text = f.read()
            if text_format == "auto":
                text_format = message_path.suffix.lower()
                if text_format.startswith("."):
                    text_format = text_format[1:]
            match text_format:
                case "txt":
                    plain_text = True
                case "html":
                    plain_text = False
                case _:
                    raise ValueError("Format invalide pour l'argument `--text-format`")
            return cls(message_text, plain_text)
        else:
            return None


class MailInfo:
    """Classe contenant les paramètres relatifs aux mails.

    ---

    Container for all mail-related settings.
    """

    ImapInfo = NamedTuple("_ImapInfo", [("hostname", str), ("port", int), ("sent_folder", str)])

    def __init__(self, config: _MailModel, message: Message | None, copy_to_imap: bool, testing: bool) -> None:
        self.smtp = config.smtp
        self.imap = self.ImapInfo(
            config.imap.hostname if config.imap and config.imap.hostname else self.smtp.hostname,
            config.imap.port if config.imap else _IMAPModel.DefaultPort,
            config.imap.sent_folder if config.imap else _IMAPModel.DefaultSentFolder,
        )
        self.username = config.username
        self._password = config.password
        self.sender_mail = config.sender_mail if config.sender_mail else self.username
        self.sender_name = config.sender_name if config.sender_name else self.username
        self.message = message
        self.copy_to_sent_folder = copy_to_imap
        self.testing = testing

    @property
    def password(self) -> str:
        """Mot de passe."""
        if not self._password:
            self._password = getpass.getpass("Mot de passe mail :")
        return self._password


def create_servers(mail_info: MailInfo) -> tuple[smtplib.SMTP, imaplib.IMAP4 | None]:
    """Crée les serveurs.

    S'il y a des erreurs, fait s'arrêter le programme et quitte.
    """
    try:
        smtp_server = smtplib.SMTP(
            host=mail_info.smtp.hostname,
            port=mail_info.smtp.port,
        )
        smtp_server.starttls()
        smtp_server.login(
            mail_info.username,
            mail_info.password,
        )
    except Exception as e:  # noqa # pyright: ignore[reportUnusedVariable]
        logger.error("Impossible de se connecter au serveur SMTP")
        # print(e)
        sys.exit(1)

    imap_server: imaplib.IMAP4 | None = None
    if mail_info.copy_to_sent_folder:
        try:
            imap_server = imaplib.IMAP4(
                mail_info.imap.hostname,
                mail_info.imap.port,
            )
            imap_server.starttls()
            imap_server.login(
                mail_info.username,
                mail_info.password,
            )
        except Exception as e:  # noqa # pyright: ignore[reportUnusedVariable]
            logger.error("Impossible de se connecter au serveur IMAP")
            smtp_server.close()
            # print(e)
            sys.exit(1)

    return smtp_server, imap_server


def message_to_subject_body(message: str) -> tuple[str, str]:
    """À partir d'un message, extrait l'objet et le corps de texte."""
    as_list = message.split("\n")
    subject = as_list[0]
    body = "\n".join(as_list[1:]).strip()  # HTML n'a que faire des \n mais le mode --plain-text en a besoin

    return subject, body


def _to_header(msg: str) -> str:
    return str(Header(msg, "utf-8"))


def _add_to_imap_server(server: imaplib.IMAP4, mail: MIMEMultipart, sent_folder: str) -> None:
    """Appelle proprement `server.append(...)`.

    ---

    Wrapper for `server.append(...)`.
    """
    server.append(
        mailbox=sent_folder,
        flags="\\Seen",
        date_time=imaplib.Time2Internaldate(time.time()),
        message=mail.as_bytes(),
    )


def _to_person_tuple(name: str) -> PersonTuple:
    return PersonTuple(
        f"'{name}'",
        f"'nom {name}'",
        f"'surnom {name}'",
        f"'email {name}'",
        [f"'liste d'autorisation {name}'"],
        [f"'liste de refus {name}'"],
    )


def test_mail_sending(mail_info: MailInfo) -> None:
    """Tester la configuration mail."""
    smtp_server, imap_server = create_servers(mail_info)
    sender = formataddr((_to_header(mail_info.sender_name), mail_info.sender_mail))

    subject = "Test de configuration Ronde de Cadeaux"
    body = "Ça a l'air de marcher :D"
    if mail_info.message:
        formatted = format_message_people(_to_person_tuple("offreureuse"), _to_person_tuple("destinataire"), mail_info.message.text)
        subject, body = message_to_subject_body(formatted)

    mail = MIMEMultipart()
    mail["From"] = sender
    mail["To"] = sender
    mail["Subject"] = _to_header(subject)
    mail.attach(MIMEText(body, "plain" if mail_info.message is None or mail_info.message.is_plain_text else "html"))

    try:
        smtp_server.sendmail(mail_info.sender_mail, mail_info.sender_mail, mail.as_string())
    except Exception:
        logger.error("Erreur d'envoi SMTP")
        smtp_server.close()
        if imap_server is not None:
            imap_server.logout()
        sys.exit(1)
    smtp_server.quit()

    if mail_info.copy_to_sent_folder:
        assert imap_server is not None
        try:
            _add_to_imap_server(imap_server, mail, mail_info.imap.sent_folder)
        except Exception:
            logger.error("Erreur de copie IMAP")
            imap_server.logout()
            sys.exit(1)
        else:
            imap_server.logout()

    logger.info("Tout a l'air de fonctionner!")


def send_mails(gifter_giftee_tuple: Draw, mail_info: MailInfo) -> None:
    """Envoi des mails."""
    assert mail_info.message

    smtp_server, imap_server = create_servers(mail_info)
    try:
        sender = formataddr((_to_header(mail_info.sender_name), mail_info.sender_mail))

        for gifter, giftee in gifter_giftee_tuple:
            assert gifter.email is not None
            mail = MIMEMultipart()
            mail["From"] = sender
            mail["To"] = formataddr((_to_header(gifter.name), gifter.email))
            formatted = format_message_people(gifter, giftee, mail_info.message.text)
            subject, body = message_to_subject_body(formatted)
            mail["Subject"] = _to_header(subject)
            mail.attach(MIMEText(body, "plain" if mail_info.message.is_plain_text else "html"))

            smtp_server.sendmail(mail_info.sender_mail, gifter.email, mail.as_string())
            if mail_info.copy_to_sent_folder:
                assert imap_server is not None
                _add_to_imap_server(imap_server, mail, mail_info.imap.sent_folder)

    except Exception as e:
        logger.error(f"Erreur : {repr(e)}")

    else:
        logger.info("L'envoi de mail a réussi.")

    finally:
        if imap_server:
            imap_server.logout()
        smtp_server.quit()


def create_mail_info(testing: bool, config_path: Path, message_path: Path | None, text_format: str, no_imap: bool) -> MailInfo:
    """Convertit les arguments relatifs aux mails venant du parser en une structure `MailInfo`.

    Délègue à `_create_mail_info`.

    Lève:
      - `ValueError` si des données invalides sont données
      - `FileNotFoundError` si un des fichiers n'existe pas

    ---

    Convert parser mail arguments into a proper `MailInfo` structure.

    Delegates to `_create_mail_info`.

    Raise:
      - `ValueError` if invalid data is given.
      - `FileNotFoundError` if one of the files doesn't exist.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Le fichier de configuration mail `{config_path}` n'existe pas")
    if message_path and not message_path.exists():
        raise FileNotFoundError(f"Le fichier de message `{message_path}` n'existe pas")

    message = Message.FromMessagePath(message_path, text_format)

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            mail_data = yaml.safe_load(f)
        except yaml.YAMLError:
            raise ValueError("Fichier de configuration mail invalide (YAML invalide)")
            # raise ValueError("Invalid mail configuration file (Ill-formed YAML)")

    return _create_mail_info(testing, mail_data, message, no_imap)


def _create_mail_info(testing: bool, mail_data: Any, message: Message | None, no_imap: bool) -> MailInfo:  # noqa: ANN401
    """Version privée, utilisée pour les tests unitaires."""
    try:
        config = _MailModel.model_validate(mail_data)
    except ValidationError:
        raise ValueError("Fichier de configuration mail invalide (non conforme au schéma)")
        # raise ValueError("Invalid mail configuration file (Invalid schema)")

    return MailInfo(
        config=config,
        message=message,
        copy_to_imap=not no_imap,
        testing=testing,
    )
