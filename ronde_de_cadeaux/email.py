"""Module relatif aux courriels.

Validation des données et envoi.
"""

import getpass
import imaplib
import smtplib
import socket
import time
from dataclasses import dataclass
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path
from typing import Any, ClassVar, NamedTuple, Self

import yaml
from dacite import from_dict

from ._unique_yaml import UniquenessError, unique_safe_load
from .logger import logger
from .people_graph_generation import Draw, DrawPair, PersonLike, PersonTuple
from .tools import EmailValidator, email_address_validator, shuffled

_BODY_TEXT_FORMAT = ["auto", "txt", "html"]


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
                "gifter_email": gifter.email,
                "giftee_id": giftee.id,
                "giftee_name": giftee.name,
                "giftee_nickname": giftee.nickname,
                "giftee_email": giftee.email,
            }
        )
    )
    return msg


@dataclass
class _SMTPConfigModel:
    hostname: str
    port: int = 587


@dataclass
class _IMAPConfigModel:
    DefaultPort: ClassVar[int] = 143
    DefaultSentFolder: ClassVar[str] = "Sent"

    hostname: str | None = None
    port: int = DefaultPort
    sent_folder: str = DefaultSentFolder


@dataclass
class _EmailModel:
    username: str
    smtp: _SMTPConfigModel
    imap: _IMAPConfigModel | None = None
    password: str | None = None
    sender_email: str | None = None
    sender_name: str | None = None
    copy_to_sent_folder: bool = True
    body_text_format: str = "auto"


class Message(NamedTuple):
    """Un message et son format."""

    subject: str
    body: str
    is_plain_text: bool = False

    @staticmethod
    def message_to_subject_body(message: str) -> tuple[str, str]:
        """À partir d'une chaîne de caractères multiligne, extrait l'objet et le corps de texte."""
        as_list = message.split("\n")
        subject = as_list[0]
        body = "\n".join(as_list[1:]).strip()  # HTML n'a que faire des \n mais le mode --plain-text en a besoin

        return subject, body

    @classmethod
    def FromMessagePath(cls, message_path: Path | None, text_format: str) -> Self | None:
        """Crée un message ou pas selon le chemin et le format précisé."""
        if message_path:
            if text_format not in _BODY_TEXT_FORMAT:
                raise ValueError(f"Le format de texte '{text_format}' n'est pas contenu dans {_BODY_TEXT_FORMAT}")
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
                    raise ValueError("Format de texte invalide")
            return cls(*cls.message_to_subject_body(message_text), plain_text)
        else:
            return None

    def formatted(self, gifter: PersonLike, giftee: PersonLike) -> Self:
        """Renvoie une version formatée du message."""
        return self._replace(
            subject=format_message_people(gifter, giftee, self.subject),
            body=format_message_people(gifter, giftee, self.body),
        )


class EmailConfig:
    """Classe contenant les paramètres relatifs aux courriels.

    ---

    Container for all email-related settings.
    """

    ImapInfo = NamedTuple("_ImapInfo", [("hostname", str), ("port", int), ("sent_folder", str)])

    def __init__(self, config: _EmailModel) -> None:
        self.smtp = config.smtp
        self.imap = self.ImapInfo(
            config.imap.hostname if config.imap and config.imap.hostname else self.smtp.hostname,
            config.imap.port if config.imap else _IMAPConfigModel.DefaultPort,
            config.imap.sent_folder if config.imap else _IMAPConfigModel.DefaultSentFolder,
        )
        self.username = config.username
        self._password = config.password
        sender_email = config.sender_email if config.sender_email else self.username
        self.sender_name = config.sender_name if config.sender_name else self.username
        self.copy_to_sent_folder = config.copy_to_sent_folder
        self.body_text_format = config.body_text_format
        if self.body_text_format not in _BODY_TEXT_FORMAT:
            raise ValueError(f"body_text_format doit avoir une valeur dans {_BODY_TEXT_FORMAT}.")

        _status, self.sender_email = email_address_validator.validate(sender_email)
        _S = EmailValidator.ValidationStatus
        match _status:
            case _S.SYNTAX_ERROR:
                raise ValueError("L'adresse courriel expéditrice n'est pas valide")
            case _S.DNS_ERROR:
                raise ValueError("La vérification DNS de l'adresse courriel expéditrice n'aboutit pas")
            case _S.UNKNOWN_DELIVERABILITY:
                logger.warning(f"""\
                    La délivrabilité de l'adresse courriel expéditrice ({self.sender_email}) n'a pas pu être vérifiée.
                    Peut-être que des erreurs auront lieu ¯\\_(ツ)_/¯
                    """)
            case _S.OK:
                pass

    @property
    def password(self) -> str:
        """Mot de passe."""
        if not self._password:
            self._password = getpass.getpass("Mot de passe courriel:")
        return self._password


@dataclass
class EmailInfo:
    """Conteneur des informations concernant les courriels."""

    config: EmailConfig
    message: Message | None
    testing: bool


class Emailer:
    """Classe qui gère la création et l'envoi de courriels."""

    class BaseError(Exception):  # noqa
        pass

    class SMTPError(BaseError):  # noqa
        pass

    class IMAPError(BaseError):  # noqa
        pass

    class MessageError(BaseError):  # noqa
        pass

    def __init__(self, email_config: EmailConfig) -> None:
        self.imap_server: imaplib.IMAP4 | None = None

        try:
            logger.debug("Ouverture du serveur SMTP...", newline=False)
            self.smtp_server = smtplib.SMTP(
                host=email_config.smtp.hostname,
                port=email_config.smtp.port,
            )
            self.smtp_server.starttls()
            self.smtp_server.login(
                email_config.username,
                email_config.password,
            )
            logger.debug("OK")

        except (socket.gaierror, TimeoutError) as e:
            raise self.SMTPError("""\
                Impossible de joindre le serveur SMTP, vérifiez votre connexion internet
                ou vos paramètres de connexion""") from e
        except Exception as e:
            raise self.SMTPError("Impossible de se connecter au serveur SMTP") from e

        if email_config.copy_to_sent_folder:
            try:
                logger.debug("Ouverture du serveur IMAP...", newline=False)
                self.imap_server = imaplib.IMAP4(
                    email_config.imap.hostname,
                    email_config.imap.port,
                )
                self.imap_server.starttls()
                self.imap_server.login(
                    email_config.username,
                    email_config.password,
                )
                logger.debug("OK")
            except (socket.gaierror, TimeoutError) as e:
                raise self.IMAPError("""\
                    Impossible de joindre le serveur IMAP, vérifiez votre connexion internet
                    ou vos paramètres de connexion""") from e
            except Exception as e:
                raise self.IMAPError("Impossible de se connecter au serveur IMAP") from e

        self.copy_to_sent_folder = email_config.copy_to_sent_folder
        self.sender_email = email_config.sender_email
        self.sender = formataddr((self._to_header(email_config.sender_name), email_config.sender_email))
        self.sent_folder = email_config.imap.sent_folder

    def __del__(self) -> None:
        self.close_servers()

    def close_servers(self) -> None:
        """Clôt proprement les serveurs SMTP et IMAP s'ils existent."""
        logger.debug("Fermeture des serveurs")

        try:
            self.smtp_server.quit()
        except Exception:
            logger.debug("- Impossible de fermer le serveur SMTP")
        else:
            logger.debug("- Serveur SMTP fermé")

        if self.imap_server:
            try:
                self.imap_server.logout()
            except Exception:
                logger.debug("- Impossible de fermer le serveur IMAP")
            else:
                logger.debug("- Serveur IMAP fermé")
        else:
            logger.debug("- Pas de serveur IMAP")

    @staticmethod
    def _to_header(msg: str) -> str:
        return str(Header(msg, "utf-8"))

    def create_and_send_email_object(self, receiver_name: str, receiver_email: str, message: Message) -> None:
        """Crée et envoie un object `MIMEMultipart` représentant le courriel."""
        try:
            email = MIMEMultipart()
            email["From"] = self.sender
            email["To"] = formataddr((self._to_header(receiver_name), receiver_email))
            email["Subject"] = self._to_header(message.subject)
            email.attach(MIMEText(message.body, "plain" if message.is_plain_text else "html"))
        except UnicodeError as e:
            raise self.MessageError("Erreur d'encodage dans le courriel") from e

        try:
            self.smtp_server.sendmail(self.sender_email, receiver_email, email.as_string())
        except smtplib.SMTPException as e:
            raise self.SMTPError(f"Impossible d'envoyer le courriel à {receiver_email}") from e

        if self.imap_server:
            try:
                self.imap_server.append(
                    mailbox=self.sent_folder,
                    flags="\\Seen",
                    date_time=imaplib.Time2Internaldate(time.time()),
                    message=email.as_bytes(),
                )
            except imaplib.IMAP4.error as e:
                raise self.IMAPError("Impossible de copier le courriel dans la boîte d'envoi") from e


def _to_person_tuple(name: str) -> PersonTuple:
    return PersonTuple(
        f"'{name}'",
        f"'nom {name}'",
        f"'surnom {name}'",
        f"'courriel {name}'",
        [f"'liste d'autorisation {name}'"],
        [f"'liste de refus {name}'"],
    )


def test_email_sending(email_info: EmailInfo) -> None:
    """Tester la configuration de l'envoi des courriels."""
    if not email_info.message:
        message = Message(
            subject="Test de configuration Ronde de Cadeaux",
            body="Ça a l'air de marcher :D",
        )
    else:
        message = email_info.message.formatted(_to_person_tuple("offreureuse"), _to_person_tuple("destinataire"))

    emailer = Emailer(email_info.config)
    try:
        emailer.create_and_send_email_object(email_info.config.sender_name, email_info.config.sender_email, message)
    finally:
        emailer.close_servers()


def send_emails(gifter_giftee_tuple: Draw, email_info: EmailInfo) -> None:
    """Envoi des courriels.

    Peut lever une `Emailer.BaseError`.
    """
    assert email_info.message
    emailer = Emailer(email_info.config)

    sent: list[str] = []
    current_draw: DrawPair | None = None
    # shuffled, comme ça l'ordre d'envoi des courriels ne permet pas d'inférer l'ordre de la ronde depuis la boîte d'envoi ;)
    try:
        for current_draw in shuffled(gifter_giftee_tuple):
            gifter, giftee = current_draw
            assert gifter.email is not None

            try:
                emailer.create_and_send_email_object(
                    gifter.name,
                    gifter.email,
                    email_info.message.formatted(gifter, giftee),
                )
            except Emailer.IMAPError:
                sent.append(gifter.email)  # L'envoi du courriel a réussi, mais on échoue après hélas
                raise
            sent.append(gifter.email)
    except Exception:
        if len(sent) > 0:
            logger.warning(f"{len(sent)} courriels ont été envoyés avant l'erreur :/")
            for address in sent:
                logger.warning(f" - {address}")
        raise
    finally:
        emailer.close_servers()


def create_email_info(config_path: Path, message_path: Path | None, testing: bool) -> EmailInfo:
    """Convertit les arguments relatifs aux courriels venant du parser en une structure `EmailInfo`.

    Lève:
      - `ValueError` si des données invalides sont données
      - `FileNotFoundError` si un des fichiers n'existe pas

    ---

    Convert parser email arguments into a proper `EmailInfo` structure.

    Raise:
      - `ValueError` if invalid data is given.
      - `FileNotFoundError` if one of the files doesn't exist.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Le fichier de configuration du serveur de messagerie `{config_path}` n'existe pas")
    if message_path and not message_path.exists():
        raise FileNotFoundError(f"Le fichier de message `{message_path}` n'existe pas")

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            email_data = unique_safe_load(f)
        except (yaml.YAMLError, UniquenessError) as e:
            raise ValueError(f"Fichier de configuration du serveur de messagerie invalide ({e})") from e

    config = _create_email_config_from_raw_data(email_data)
    message = Message.FromMessagePath(message_path, config.body_text_format)
    return EmailInfo(config, message, testing)


def _create_email_config_from_raw_data(email_data: Any) -> EmailConfig:  # noqa: ANN401
    try:
        config = from_dict(_EmailModel, email_data)
    except Exception as e:
        raise ValueError("Fichier de configuration du serveur de messagerie invalide (non conforme au schéma)") from e
    return EmailConfig(config)
