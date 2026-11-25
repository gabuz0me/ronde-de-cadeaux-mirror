from base import RondeTest

from ronde_de_cadeaux.parser import ParserArgs


class ParserTest(RondeTest):
    def test_email_test_no_auth(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args="--test-email")

    def test_at_least_one_action(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--people", self.example_people_yaml])

    def test_auth_no_message(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--email-config", self.example_email_config])

    def test_no_input_file(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args="--show")

    def test_already_existing_file(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--people", self.example_people_yaml, "--output", self.get_existing_file(".txt")])

    def test_non_existing_files(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--test-email", "--email-config", self.get_non_existing_file(".yaml")])

        with self.assertRaises(ValueError):
            _ = ParserArgs(custom_args=["--people", self.get_non_existing_file(".yaml"), "--show"])

    def test_test_email_with_people(self):
        with self.assertRaises(ValueError):
            _ = ParserArgs(
                custom_args=[
                    "--test-email",
                    "--email-config",
                    self.example_email_config,
                    "--people",
                    self.example_people_csv,
                ]
            )

    def test_correct_arguments_yaml(self):
        output = self.get_existing_file(".txt")
        args = ParserArgs(
            custom_args=[
                "--people",
                self.example_people_yaml,
                "--output",
                output,
                "--overwrite",
                "--email-config",
                self.example_email_config,
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
        self.assertIsNotNone(args.email)
        assert args.email is not None
        self.assertTrue(args.email.config.copy_to_sent_folder)

    def test_correct_arguments_csv(self):
        output = self.get_non_existing_file(".txt")
        args = ParserArgs(
            custom_args=[
                "--people",
                self.example_people_csv,
                "--output",
                output,
                "--message",
                self.example_message_html,
                "--show",
            ]
        )
        self.assertTrue(args.show)
        self.assertEqual(str(args.output), output)
        self.assertIsNone(args.email)
