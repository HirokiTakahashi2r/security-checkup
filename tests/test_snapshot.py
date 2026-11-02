import json
import tempfile
import unittest
from pathlib import Path

from security_checkup import snapshot


class DiffTest(unittest.TestCase):
    def test_lists_report_added_and_removed(self):
        changes = snapshot.diff({"a": {"apps": ["x", "y"]}}, {"a": {"apps": ["y", "z"]}})
        self.assertEqual(changes, {"a.apps": {"added": ["z"], "removed": ["x"]}})

    def test_values_report_before_and_after(self):
        changes = snapshot.diff({"fw": {"on": True}}, {"fw": {"on": False}, "new": 1})
        self.assertEqual(changes, {"fw.on": {"before": True, "after": False}, "new": {"before": None, "after": 1}})

    def test_no_changes(self):
        self.assertEqual(snapshot.diff({"a": [1]}, {"a": [1]}), {})


class WriteTest(unittest.TestCase):
    def test_compares_with_latest_earlier_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            (folder / "2026-01-01.json").write_text(json.dumps({"collected_at": "x", "a": 1}))
            (folder / "2026-02-01.json").write_text(json.dumps({"collected_at": "y", "a": 2}))
            (folder / "2026-03-01.json").write_text(json.dumps({"collected_at": "z", "a": 9}))
            snap = {"collected_at": "now", "a": 3}
            out = snapshot.write(folder, "2026-02-15", snap)
            self.assertEqual(snap["diff_from"], "2026-02-01")
            self.assertEqual(snap["changes"], {"a": {"before": 2, "after": 3}})
            self.assertEqual(out.stat().st_mode & 0o777, 0o600)

    def test_first_snapshot_has_no_diff(self):
        with tempfile.TemporaryDirectory() as d:
            snap = {"collected_at": "now"}
            snapshot.write(Path(d) / "snapshots", "2026-01-01", snap)
            self.assertNotIn("diff_from", snap)


if __name__ == "__main__":
    unittest.main()
