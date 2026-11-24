"""Module relatif aux courriels.

Validation des données et envoi.
"""

import getpass
import imaplib
import logging
import os
import smtplib
import socket
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar, NamedTuple, Self, TypeVar

import yaml
from dacite import from_dict
from tqdm import tqdm

from ._unique_yaml import UniquenessError, unique_safe_load
from .i18n import _, ngettext
from .logger import Color, colored, logger
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
    username: str
    hostname: str
    password: str | None = None
    port: int = 587


@dataclass
class _IMAPConfigModel:
    # on utilise les ClassVar pour accéder aux valeurs par défaut hors de la classe (si `_EmailModel` n'a pas de `_IMAPConfigModel`)
    DefaultPort: ClassVar[int] = 143
    DefaultSentFolder: ClassVar[str] = "Sent"

    hostname: str | None = None
    port: int = DefaultPort
    sent_folder: str = DefaultSentFolder
    username: str | None = None
    password: str | None | bool = None


@dataclass
class _EmailConfigModel:
    smtp: _SMTPConfigModel
    imap: _IMAPConfigModel | None = None
    from_email: str | None = None
    from_name: str | None = None
    test_to_email: str | None = None
    copy_to_sent_folder: bool = True
    body_text_format: str = "auto"


class _SMTPView:
    """Un objet *vue* sur les paramètres SMTP."""

    def __init__(self, config_model_smtp: _SMTPConfigModel) -> None:
        self._smtp = config_model_smtp

    @property
    def username(self) -> str:
        return self._smtp.username

    @property
    def hostname(self) -> str:
        return self._smtp.hostname

    @property
    def port(self) -> int:
        return self._smtp.port

    @cached_property
    def password(self) -> str:
        if self._smtp.password:
            return self._smtp.password
        if password := os.environ.get("RONDE_PASSWORD_SMTP"):
            return password
        try:
            password = getpass.getpass(_("Mot de passe %(server)s :") % {"server": "SMTP"})
        except (EOFError, getpass.GetPassWarning) as e:
            raise ValueError(_("Impossible d'acquérir le mot de passe")) from e
        else:
            return password


class _IMAPView:
    """Un objet *vue* sur les paramètres IMAP."""

    def __init__(self, imap_config: _IMAPConfigModel | None, smtp_view: _SMTPView) -> None:
        self._imap = imap_config
        self._smtp = smtp_view

    @property
    def hostname(self) -> str:
        return (self._imap.hostname if self._imap else None) or self._smtp.hostname

    @property
    def username(self) -> str:
        return (self._imap.username if self._imap else None) or self._smtp.username

    @property
    def sent_folder(self) -> str:
        return (self._imap.sent_folder if self._imap else None) or _IMAPConfigModel.DefaultSentFolder

    @property
    def port(self) -> int:
        return (self._imap.port if self._imap else None) or _IMAPConfigModel.DefaultPort

    @cached_property
    def password(self) -> str:
        value: str | bool = self._imap.password if self._imap and self._imap.password else False  # On récupère la valeur, None->False
        if isinstance(value, str):
            return value
        if value:
            try:
                password = getpass.getpass(_("Mot de passe %(server)s :") % {"server": "IMAP"})
            except (EOFError, getpass.GetPassWarning) as e:
                raise ValueError(_("Impossible d'acquérir le mot de passe")) from e
            else:
                return password
        if password := os.environ.get("RONDE_PASSWORD_IMAP"):
            return password
        return self._smtp.password


class EmailConfig:
    """Classe contenant les paramètres relatifs aux courriels.

    On dépile `_SMTPConfigModel` et `_IMAPConfigModel` : Les champs qui valent None
    Sont évalués de manière lazy

    ---

    Container for all email-related settings.
    """

    def __init__(self, config: _EmailConfigModel) -> None:
        # Vues des serveurs
        self.smtp = _SMTPView(config.smtp)
        self.imap = _IMAPView(config.imap, self.smtp)

        # Champs à la racine
        self.from_name = config.from_name or self.smtp.username
        self.from_email = (config.from_email or self.smtp.username).strip()
        self.test_to_email = (config.test_to_email or self.from_email).strip()
        self.copy_to_sent_folder = config.copy_to_sent_folder
        self.body_text_format = config.body_text_format
        if self.body_text_format not in _BODY_TEXT_FORMAT:
            raise ValueError(
                _("Le champ 'body_text_format' doit avoir une valeur dans %(text_format_list)s")  #
                % {"text_format_list": _BODY_TEXT_FORMAT}
            )

        # Validation des adresses courriel
        if self.test_to_email != self.from_email:
            self.test_to_email = self.validated_email(self.test_to_email, _("expéditrice"))
        self.from_email = self.validated_email(self.from_email, _("de réception des tests"))

    @staticmethod
    def validated_email(email_address: str, address_kind: str) -> str:
        """Valide un adresse courriel, peut afficher dans le logger.

        Lève une `ValueError` si l'adresse courriel n'est pas valide.
        """  # noqa
        _S = EmailValidator.ValidationStatus
        _status, validated = email_address_validator.validate(email_address)
        match _status:
            case _S.SYNTAX_ERROR:
                raise ValueError(
                    _("L'adresse courriel %(address_kind)s '%(email)s' n'est pas valide")
                    % {"email": email_address, "address_kind": address_kind}
                )
            case _S.DNS_ERROR:
                raise ValueError(
                    _("La vérification DNS de l'adresse courriel %(address_kind)s '%(email)s' n'aboutit pas")
                    % {"email": email_address, "address_kind": address_kind}
                )
            case _S.UNKNOWN_DELIVERABILITY:
                logger.warning(
                    _("La délivrabilité de l'adresse courriel %(address_kind)s '%(email)s' n'a pas pu être vérifiée. %(maybe_errors)s")
                    % {
                        "email": email_address,
                        "address_kind": address_kind,
                        "maybe_errors": _("Peut-être que des erreurs auront lieu ¯\\_(ツ)_/¯"),
                    }
                )
            case _S.OK:
                pass
        return validated


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
        body = "\n".join(as_list[1:]).strip()  # HTML n'a que faire des \n mais le format plain text en a besoin

        return subject, body

    @classmethod
    def FromMessagePath(cls, message_path: Path | None, text_format: str) -> Self | None:
        """Crée un message ou pas selon le chemin et le format précisé."""
        if message_path:
            if text_format not in _BODY_TEXT_FORMAT:
                raise ValueError(
                    _("Le format de texte '%(text_format)s' n'est pas contenu dans %(text_format_list)s")
                    % {"text_format": text_format, "text_format_list": _BODY_TEXT_FORMAT}
                )
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
                    raise ValueError(_("Format de texte invalide"))
            return cls(*cls.message_to_subject_body(message_text), plain_text)
        else:
            return None

    def formatted(self, gifter: PersonLike, giftee: PersonLike) -> Self:
        """Renvoie une version formatée du message."""
        return self._replace(
            subject=format_message_people(gifter, giftee, self.subject),
            body=format_message_people(gifter, giftee, self.body),
        )


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

        _CONNECTION_ERROR = _("""\
            Impossible de joindre le serveur %(server)s, vérifier la connexion internet
            ou les paramètres de connexion""")

        try:
            logger.debug(_("Ouverture du serveur %(server)s...") % {"server": "SMTP"})
            self.smtp_server = smtplib.SMTP(
                host=email_config.smtp.hostname,
                port=email_config.smtp.port,
            )
            self.smtp_server.starttls()
            self.smtp_server.login(
                email_config.smtp.username,
                email_config.smtp.password,
            )

        except (socket.gaierror, TimeoutError) as e:
            raise self.SMTPError(_CONNECTION_ERROR % {"server": "SMTP"}) from e
        except Exception as e:
            raise self.SMTPError(_("Impossible de se connecter au serveur %(server)s") % {"server": "SMTP"}) from e

        if email_config.copy_to_sent_folder:
            try:
                logger.debug(_("Ouverture du serveur %(server)s...") % {"server": "IMAP"})
                self.imap_server = imaplib.IMAP4(
                    email_config.imap.hostname,
                    email_config.imap.port,
                )
                self.imap_server.starttls()
                self.imap_server.login(
                    email_config.imap.username,
                    email_config.imap.password,
                )
            except (socket.gaierror, TimeoutError) as e:
                raise self.IMAPError(_CONNECTION_ERROR % {"server": "IMAP"}) from e
            except Exception as e:
                raise self.IMAPError(_("Impossible de se connecter au serveur %(server)s") % {"server": "IMAP"}) from e

        self.copy_to_sent_folder = email_config.copy_to_sent_folder
        self.from_email = email_config.from_email
        self.sender = formataddr((self._to_header(email_config.from_name), email_config.from_email))
        self.sent_folder = email_config.imap.sent_folder

    def close_servers(self) -> None:
        """Clôt proprement les serveurs SMTP et IMAP s'ils existent."""
        logger.debug(_("Fermeture des serveurs"))

        try:
            self.smtp_server.quit()
        except Exception:
            logger.debug(_("- Impossible de fermer le serveur %(server)s") % {"server": "SMTP"})
        else:
            logger.debug(_("- Serveur %(server)s fermé") % {"server": "SMTP"})

        if self.imap_server:
            try:
                self.imap_server.logout()
            except Exception:
                logger.debug(_("- Impossible de fermer le serveur %(server)s") % {"server": "IMAP"})
            else:
                logger.debug(_("- Serveur %(server)s fermé") % {"server": "IMAP"})
        else:
            logger.debug(_("- Pas de serveur %(server)s") % {"server": "IMAP"})

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
            raise self.MessageError(_("Erreur d'encodage dans le courriel")) from e

        try:
            self.smtp_server.sendmail(self.from_email, receiver_email, email.as_string())
        except smtplib.SMTPException as e:
            raise self.SMTPError(
                _("Impossible d'envoyer le courriel à %(name)s (%(email)s)")
                % {"receiver_name": receiver_name, "email_address": receiver_email}
            ) from e

        if self.imap_server:
            try:
                self.imap_server.append(
                    mailbox=self.sent_folder,
                    flags="\\Seen",
                    date_time=imaplib.Time2Internaldate(time.time()),
                    message=email.as_bytes(),
                )
            except imaplib.IMAP4.error as e:
                raise self.IMAPError(_("Impossible de copier le courriel dans la boîte d'envoi")) from e


def _to_person_tuple(name: str) -> PersonTuple:
    return PersonTuple(
        f"'{name}'",
        f"'{_('nom')} {name}'",
        f"'{_('surnom')} {name}'",
        f"'{_('adresse courriel')} {name}'",
        [f"'{_("liste d'autorisation")} {name}'"],
        [f"'{_('liste de rejet')} {name}'"],
    )


def test_email_sending(email_info: EmailInfo) -> None:
    """Tester la configuration de l'envoi des courriels."""
    if not email_info.message:
        message = Message(
            subject=_("Test de configuration Ronde de Cadeaux"),
            body=_("Ça a l'air de marcher :D"),
        )
    else:
        message = email_info.message.formatted(_to_person_tuple(_("offreureuse")), _to_person_tuple(_("destinataire")))

    emailer = Emailer(email_info.config)
    try:
        emailer.create_and_send_email_object("", email_info.config.test_to_email, message)
    finally:
        emailer.close_servers()


T = TypeVar("T")


def _email_progress_bar(iterable: Iterable[T]) -> Iterable[T] | tqdm[T]:  # noqa
    """Barre de progression custom pour les courriels."""
    if logger.level > logging.INFO:
        return iterable

    bar_format = colored("{desc} {n_fmt:>2}/{total_fmt} |{bar}|", Color.GREEN)

    return tqdm(
        iterable=iterable,
        desc=_("Envoi des courriels :"),
        dynamic_ncols=True,
        bar_format=bar_format,
        file=sys.stderr,  # C'est la valeur par défaut mais voilà
    )


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
        for current_draw in _email_progress_bar(shuffled(gifter_giftee_tuple)):
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
        if (nb := len(sent)) > 0:
            logger.warning(
                ngettext("%(nb)s courriel a été envoyé avant l'erreur :/", "%(nb)s courriels ont été envoyés avant l'erreur :/", nb)
                % {"nb": nb}
            )
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
        raise FileNotFoundError(_("Le fichier de configuration du serveur de messagerie '%(path)s' n'existe pas") % {"path": config_path})
    if message_path and not message_path.exists():
        raise FileNotFoundError(_("Le fichier de message '%(path)s' n'existe pas") % {"path": message_path})

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            email_data = unique_safe_load(f)
        except (yaml.YAMLError, UniquenessError) as e:
            raise ValueError(_("Fichier de configuration du serveur de messagerie invalide (%(error)s)") % {"error": e}) from e

    config = _create_email_config_from_raw_data(email_data)
    message = Message.FromMessagePath(message_path, config.body_text_format)
    return EmailInfo(config, message, testing)


def _create_email_config_from_raw_data(email_data: Any) -> EmailConfig:  # noqa: ANN401
    try:
        config = from_dict(_EmailConfigModel, email_data)
    except Exception as e:
        raise ValueError(
            _("Fichier de configuration du serveur de messagerie invalide (%(error)s)") % {"error": _("non conforme au schéma")}
        ) from e
    return EmailConfig(config)
