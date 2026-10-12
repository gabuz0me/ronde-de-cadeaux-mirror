from pathlib import Path
from textwrap import dedent

import yaml

from ronde_de_cadeaux.mail import MailInfo, Message, _create_mail_info, format_message_people, message_to_subject_body
from ronde_de_cadeaux.people_graph_generation import _create_people_and_groups_info
from tests.base import RondeTest
from tests.test_people import YAML_PEOPLE_MAXIMAL

MESSAGE = """\
SUBJECT IS HERE

Text message is here
and here,

and even here.
"""

MINIMAL = """\
smtp:
    hostname: "server.abc"
username: "username@server.abc"
password: "xxx"
"""

MAXIMAL = """\
smtp:
    hostname: "smtp.server.abc"
    port: 123
imap:
    hostname: "imap.server.abc"
    port: 456
    sent_folder: "custom_sent_folder"
username: "username@server.abc"
password: "xxx"
sender_mail: "custom_mail"
sender_name: "custom_name"
"""

INVALID = """\
smtt:
    hotsname: "srever.abc"
"""


class MailTest(RondeTest):
    @staticmethod
    def to_mail_info(data_str: str) -> MailInfo:
        data = yaml.safe_load(data_str)
        return _create_mail_info(
            testing=True,  # Pas de demande de message
            mail_data=data,
            message=None,
            no_imap=False,
        )

    def test_minimal(self):
        mail_info = self.to_mail_info(MINIMAL)
        self.assertEqual(mail_info.testing, True)
        self.assertEqual(mail_info.copy_to_sent_folder, True)

        self.assertEqual(mail_info.smtp.hostname, "server.abc")
        self.assertEqual(mail_info.smtp.port, 587)
        self.assertEqual(mail_info.imap.hostname, "server.abc")
        self.assertEqual(mail_info.imap.port, 143)
        self.assertEqual(mail_info.imap.sent_folder, "Sent")

        self.assertEqual(mail_info.username, "username@server.abc")
        self.assertEqual(mail_info.password, "xxx")
        self.assertEqual(mail_info.sender_mail, "username@server.abc")
        self.assertEqual(mail_info.sender_name, "username@server.abc")

    def test_maximal(self):
        mail_info = self.to_mail_info(MAXIMAL)
        self.assertEqual(mail_info.testing, True)
        self.assertEqual(mail_info.copy_to_sent_folder, True)

        self.assertEqual(mail_info.smtp.hostname, "smtp.server.abc")
        self.assertEqual(mail_info.smtp.port, 123)
        self.assertEqual(mail_info.imap.hostname, "imap.server.abc")
        self.assertEqual(mail_info.imap.port, 456)
        self.assertEqual(mail_info.imap.sent_folder, "custom_sent_folder")

        self.assertEqual(mail_info.username, "username@server.abc")
        self.assertEqual(mail_info.password, "xxx")
        self.assertEqual(mail_info.sender_mail, "custom_mail")
        self.assertEqual(mail_info.sender_name, "custom_name")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            self.to_mail_info(INVALID)

    def test_text_format(self):
        file_txt = Path(self.get_existing_file(".txt", "Text File"))
        file_html = Path(self.get_existing_file(".html", "HTML File"))
        file_pdf = Path(self.get_existing_file(".pdf", "PDF File"))

        self.assertIsNone(Message.FromMessagePath(None, "auto"))
        self.assertIsNone(Message.FromMessagePath(None, "txt"))
        self.assertIsNone(Message.FromMessagePath(None, "html"))
        self.assertIsNone(Message.FromMessagePath(None, "other"))

        self.assertTrue((msg := Message.FromMessagePath(file_txt, "txt")) and msg.is_plain_text)
        self.assertFalse((msg := Message.FromMessagePath(file_txt, "html")) and msg.is_plain_text)
        self.assertTrue((msg := Message.FromMessagePath(file_txt, "auto")) and msg.is_plain_text)
        with self.assertRaises(ValueError):
            Message.FromMessagePath(file_txt, "other")

        self.assertTrue((msg := Message.FromMessagePath(file_html, "txt")) and msg.is_plain_text)
        self.assertFalse((msg := Message.FromMessagePath(file_html, "html")) and msg.is_plain_text)
        self.assertFalse((msg := Message.FromMessagePath(file_html, "auto")) and msg.is_plain_text)
        with self.assertRaises(ValueError):
            Message.FromMessagePath(file_html, "other")

        self.assertTrue((msg := Message.FromMessagePath(file_pdf, "txt")) and msg.is_plain_text)
        self.assertFalse((msg := Message.FromMessagePath(file_pdf, "html")) and msg.is_plain_text)
        with self.assertRaises(ValueError):
            Message.FromMessagePath(file_pdf, "auto")
        with self.assertRaises(ValueError):
            Message.FromMessagePath(file_pdf, "other")

    def test_mail_subject_body(self):
        subject, body = message_to_subject_body(MESSAGE)
        self.assertEqual(subject, "SUBJECT IS HERE")
        self.assertEqual(
            body,
            dedent("""\
                Text message is here
                and here,

                and even here.
            """).strip(),
        )

    def test_format_message_people(self):
        data = yaml.safe_load(YAML_PEOPLE_MAXIMAL)
        people = _create_people_and_groups_info(data)

        gifter = people.id_to_person["Alice"]
        giftee = people.id_to_person["Bob"]

        template = dedent("""\
            {gifter_id}
            {gifter_name}
            {gifter_nickname}
            {gifter_mail}
            {giftee_id}
            {giftee_name}
            {giftee_nickname}
            {giftee_mail}
            {untouched}
        """)

        result = dedent("""\
            Alice
            Alice Ecila
            Al
            alice@eci.la
            Bob
            Robert Trebor
            Bobby
            robert@treb.or
            {untouched}
        """)
        self.assertEqual(
            format_message_people(gifter, giftee, template),
            result,
        )
