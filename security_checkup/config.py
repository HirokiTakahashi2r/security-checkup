"""Locate the results folder and load the machine-specific settings in results/config.json."""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"
SNAPSHOTS = RESULTS / "snapshots"
CONFIG = RESULTS / "config.json"
TODO = RESULTS / "todo.md"
PRIVATE_PATTERNS = RESULTS / "private-patterns.txt"

DEFAULTS = {
    "scan_roots": [],
    "ssh_key_dirs": ["~/.ssh"],
    "iam_checks": [],
    "node_version_file": None,
    "extra_secret_scans": {},
}


def load(path=CONFIG):
    try:
        with open(path) as f:
            user = json.load(f)
    except FileNotFoundError:
        user = {}
    unknown = set(user) - set(DEFAULTS)
    if unknown:
        raise SystemExit(f"{path}: unknown keys: {', '.join(sorted(unknown))}")
    return {**DEFAULTS, **user}
