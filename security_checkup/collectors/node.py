"""Locate the nvm default Node and the VS Code CLI, which several categories need."""

import glob
import shutil
from pathlib import Path

from ..util import HOME, IS_MACOS, read_text

NVM_VERSIONS = HOME / ".nvm/versions/node"
VSCODE_MAC = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"


def nvm_default():
    alias = read_text(HOME / ".nvm/alias/default")
    if alias is None:
        return None
    v = alias.strip().lstrip("v")
    for cand in sorted(glob.glob(str(NVM_VERSIONS / f"v{v}*")), reverse=True):
        return Path(cand).name
    return alias.strip()


def vscode_cli():
    if IS_MACOS and Path(VSCODE_MAC).exists():
        return VSCODE_MAC
    return shutil.which("code")
