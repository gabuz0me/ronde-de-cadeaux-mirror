from base import RondeTest

from ronde_de_cadeaux.parser import ParserArgs


class ParserTest(RondeTest):
    def test_mail_test_no_auth(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args="--test-mail")

    def test_at_least_one_action(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["-i", self.people])

    def test_auth_no_message(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["-a", self.mail])

    def test_no_input_file(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args="-s")

    def test_already_existing_file(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["-i", self.people, "-o", self.existing_file])

    def test_correct_arguments(self):
        args = ParserArgs(
            custom_args=[
                "--input",
                self.people,
                "--output",
                self.existing_file,
                "--force",
                "--auth",
                self.mail,
                "--message",
                self.message,
                "--show",
                "--seed",
                "42",
            ]
        )
        self.assertEqual(args.seed, "42")
        self.assertTrue(args.show)
        self.assertEqual(str(args.output), self.existing_file)
        self.assertIsNotNone(args.mail)
        assert args.mail is not None
        self.assertTrue(args.mail.copy_to_sent_folder)
