"""Small helpers shared by the collectors."""

import json
import os
import platform
import subprocess
from pathlib import Path

HOME = Path.home()
IS_MACOS = platform.system() == "Darwin"


def unsupported():
    return {"unsupported": platform.system()}


def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def lines(text):
    return sorted(l.strip() for l in (text or "").splitlines() if l.strip())


def listdir(path, suffix=None):
    try:
        names = os.listdir(path)
    except OSError:
        return None
    return sorted(n for n in names if not n.startswith(".") and (suffix is None or n.endswith(suffix)))


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def read_text(path):
    try:
        return Path(path).read_text()
    except OSError:
        return None


def tilde(path):
    s = str(path)
    return "~" + s[len(str(HOME)):] if s.startswith(str(HOME)) else s


def expand(path):
    return Path(os.path.expanduser(path))
