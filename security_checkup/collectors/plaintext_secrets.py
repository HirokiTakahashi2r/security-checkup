"""Counts of secret-looking strings in shell history, AI tool logs and settings. Values are never stored."""

import glob

from ..secrets import scan_files
from ..util import HOME, expand
from .ai_tools import permission_files


def collect(cfg):
    out = {
        "shell_history": scan_files([HOME / ".zsh_history", HOME / ".bash_history"]),
        "claude_logs": scan_files(glob.glob(str(HOME / ".claude/projects/**/*.jsonl"), recursive=True)),
        "codex_logs": scan_files(glob.glob(str(HOME / ".codex/sessions/**/*.jsonl"), recursive=True)),
        "claude_settings": scan_files(permission_files(cfg)),
    }
    for name, patterns in cfg["extra_secret_scans"].items():
        out[name] = scan_files([p for pat in patterns for p in glob.glob(str(expand(pat)), recursive=True)])
    return out
