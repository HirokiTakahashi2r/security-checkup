import json
import tempfile
import unittest
from pathlib import Path

from security_checkup import config


class LoadTest(unittest.TestCase):
    def test_missing_file_gives_empty_defaults(self):
        cfg = config.load(Path("/nonexistent/config.json"))
        self.assertEqual(cfg["iam_checks"], [])
        self.assertEqual(cfg["scan_roots"], [])
        self.assertIsNone(cfg["node_version_file"])

    def test_user_values_override_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps({"scan_roots": ["~/src"]}))
            cfg = config.load(p)
            self.assertEqual(cfg["scan_roots"], ["~/src"])
            self.assertEqual(cfg["ssh_key_dirs"], ["~/.ssh"])

    def test_unknown_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.json"
            p.write_text(json.dumps({"scan_root": ["typo"]}))
            with self.assertRaises(SystemExit):
                config.load(p)

    def test_example_config_is_valid(self):
        config.load(config.REPO / "config.example.json")


if __name__ == "__main__":
    unittest.main()
