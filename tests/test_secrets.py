import tempfile
import unittest
from pathlib import Path

from security_checkup import secrets

FAKE_AWS = "AKIA" + "ABCDEFGHIJKLMNOP"
FAKE_WEBHOOK = "https://hooks.slack.com/services/" + "T000/B000/" + "x" * 24


class RedactTest(unittest.TestCase):
    def test_hides_secret_values(self):
        out = secrets.redact(f"curl -d '{{}}' {FAKE_WEBHOOK} && echo {FAKE_AWS}")
        self.assertNotIn(FAKE_AWS, out)
        self.assertNotIn("x" * 24, out)
        self.assertIn("<redacted:aws_access_key_id>", out)
        self.assertIn("<redacted:slack_webhook>", out)

    def test_leaves_plain_commands(self):
        self.assertEqual(secrets.redact("bash ~/.claude/hooks/a.sh session"), "bash ~/.claude/hooks/a.sh session")


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patterns = Path(self.tmp.name) / "private-patterns.txt"
        self.orig = secrets.config.PRIVATE_PATTERNS
        secrets.config.PRIVATE_PATTERNS = self.patterns

    def tearDown(self):
        secrets.config.PRIVATE_PATTERNS = self.orig
        self.tmp.cleanup()

    def test_blocks_when_pattern_file_is_missing(self):
        self.assertEqual(secrets.check({"a.py": "print(1)"}), 1)

    def test_ci_mode_runs_without_pattern_file(self):
        self.assertEqual(secrets.check({"a.py": "print(1)"}, require_private=False), 0)
        self.assertEqual(secrets.check({"a.py": f"KEY = '{FAKE_AWS}'"}, require_private=False), 1)
        self.assertEqual(secrets.check({"results/todo.md": ""}, require_private=False), 1)

    def test_blocks_private_values_case_insensitively(self):
        self.patterns.write_text("# comment\nAcme-Corp\n")
        self.assertEqual(secrets.check({"a.py": "root = '~/work/acme-corp'"}), 1)
        self.assertEqual(secrets.check({"acme-corp.md": "hello"}), 1)
        self.assertEqual(secrets.check({"commit message": "Fix acme-corp path"}), 1)

    def test_blocks_secret_shapes_unless_allowlisted(self):
        self.patterns.write_text("acme-corp\n")
        self.assertEqual(secrets.check({"a.py": f"KEY = '{FAKE_AWS}'"}), 1)
        self.assertEqual(secrets.check({"a.py": f"KEY = '{FAKE_AWS}'  # {secrets.ALLOW_MARKER}"}), 0)

    def test_blocks_results_folder(self):
        self.patterns.write_text("acme-corp\n")
        self.assertEqual(secrets.check({"results/todo.md": "nothing private"}), 1)

    def test_passes_clean_changes(self):
        self.patterns.write_text("acme-corp\n")
        self.assertEqual(secrets.check({"a.py": "print('hello')"}), 0)


if __name__ == "__main__":
    unittest.main()
