"""Pending OS and Homebrew updates, Node and Python versions, VS Code extension versions."""

import re
import shutil

from ..util import HOME, IS_MACOS, expand, lines, listdir, read_text, run
from .node import NVM_VERSIONS, nvm_default, vscode_cli


def expected_node(path):
    text = read_text(expand(path)) if path else None
    m = re.search(r"\bnode:v?(\d+(?:\.\d+)*)", text or "")
    return f"v{m.group(1)}" if m else None


def collect(cfg):
    out = {}
    if IS_MACOS:
        sw = run(["softwareupdate", "-l"], timeout=180)
        out["macos"] = run(["sw_vers", "-productVersion"])
        out["macos_updates"] = [l for l in lines(sw) if l.startswith("* Label:")] if sw is not None else None
    if shutil.which("brew"):
        outdated = run(["brew", "outdated", "--quiet"], timeout=180)
        out["brew_outdated"] = lines(outdated) if outdated is not None else None
    code = vscode_cli()
    out.update({
        "node_versions": listdir(NVM_VERSIONS),
        "node_default": nvm_default(),
        "node_expected": expected_node(cfg["node_version_file"]),
        "python3": run(["python3", "--version"]),
        "uv_pythons": listdir(HOME / ".local/share/uv/python"),
        "vscode_extensions": lines(run([code, "--list-extensions", "--show-versions"])) if code else None,
    })
    return out
