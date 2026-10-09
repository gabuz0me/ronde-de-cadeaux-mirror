from base import RondeTest

from ronde_de_cadeaux.parser import ParserArgs


class ParserTest(RondeTest):
    def test_mail_test_no_auth(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args="--test-mail")

    def test_at_least_one_action(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--input", self.example_people])

    def test_auth_no_message(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--auth", self.example_mail])

    def test_no_input_file(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args="--show")

    def test_already_existing_file(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--input", self.example_people, "--output", self.get_existing_file(".txt")])

    def test_non_existing_files(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--test-mail", "--auth", self.get_non_existing_file(".yaml")])

        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--input", self.get_non_existing_file(".yaml"), "--show"])

    def test_correct_arguments(self):
        output = self.get_existing_file(".txt")
        args = ParserArgs(
            custom_args=[
                "--input",
                self.example_people,
                "--output",
                output,
                "--force",
                "--auth",
                self.example_mail,
                "--message",
                self.example_message_html,
                "--show",
                "--seed",
                "42",
            ]
        )
        self.assertEqual(args.seed, "42")
        self.assertTrue(args.show)
        self.assertEqual(str(args.output), output)
        self.assertIsNotNone(args.mail)
        assert args.mail is not None
        self.assertTrue(args.mail.copy_to_sent_folder)
