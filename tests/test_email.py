from pathlib import Path
from textwrap import dedent

from ronde_de_cadeaux._unique_yaml import unique_safe_load
from ronde_de_cadeaux.email import EmailInfo, Message, _create_email_config_from_raw_data, format_message_people
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
sender_email: "username_email@server.abc"
sender_name: "custom_name"
"""

INVALID = """\
smtt:
    hotsname: "srever.abc"
"""


class EmailTest(RondeTest):
    @staticmethod
    def to_email_info(data_str: str) -> EmailInfo:
        data = unique_safe_load(data_str)
        return EmailInfo(
            config=_create_email_config_from_raw_data(data),
            message=None,
            testing=True,  # Pas de demande de message
        )

    def test_minimal(self):
        email_info = self.to_email_info(MINIMAL)
        self.assertEqual(email_info.testing, True)
        self.assertEqual(email_info.config.copy_to_sent_folder, True)

        self.assertEqual(email_info.config.smtp.hostname, "server.abc")
        self.assertEqual(email_info.config.smtp.port, 587)
        self.assertEqual(email_info.config.imap.hostname, "server.abc")
        self.assertEqual(email_info.config.imap.port, 143)
        self.assertEqual(email_info.config.imap.sent_folder, "Sent")

        self.assertEqual(email_info.config.username, "username@server.abc")
        self.assertEqual(email_info.config.password, "xxx")
        self.assertEqual(email_info.config.sender_email, "username@server.abc")
        self.assertEqual(email_info.config.sender_name, "username@server.abc")

    def test_maximal(self):
        email_info = self.to_email_info(MAXIMAL)
        self.assertEqual(email_info.testing, True)
        self.assertEqual(email_info.config.copy_to_sent_folder, True)

        self.assertEqual(email_info.config.smtp.hostname, "smtp.server.abc")
        self.assertEqual(email_info.config.smtp.port, 123)
        self.assertEqual(email_info.config.imap.hostname, "imap.server.abc")
        self.assertEqual(email_info.config.imap.port, 456)
        self.assertEqual(email_info.config.imap.sent_folder, "custom_sent_folder")

        self.assertEqual(email_info.config.username, "username@server.abc")
        self.assertEqual(email_info.config.password, "xxx")
        self.assertEqual(email_info.config.sender_email, "username_email@server.abc")
        self.assertEqual(email_info.config.sender_name, "custom_name")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            self.to_email_info(INVALID)

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

    def test_email_subject_body(self):
        subject, body = Message.message_to_subject_body(MESSAGE)
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
        data = unique_safe_load(YAML_PEOPLE_MAXIMAL)
        people = _create_people_and_groups_info(data)

        gifter = people.id_to_person["Alice"]
        giftee = people.id_to_person["Bob"]

        template = dedent("""\
            {gifter_id}
            {gifter_name}
            {gifter_nickname}
            {gifter_email}
            {giftee_id}
            {giftee_name}
            {giftee_nickname}
            {giftee_email}
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
