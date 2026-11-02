"""Things installed or started automatically: launchd jobs, apps, packages, extensions."""

import shutil

from ..util import HOME, IS_MACOS, lines, listdir, run
from .node import NVM_VERSIONS, nvm_default, vscode_cli


def macos_items():
    return {
        "launch_agents_user": listdir(HOME / "Library/LaunchAgents"),
        "launch_agents_system": listdir("/Library/LaunchAgents"),
        "launch_daemons": listdir("/Library/LaunchDaemons"),
        "privileged_helpers": listdir("/Library/PrivilegedHelperTools"),
        "applications": listdir("/Applications", ".app"),
        "user_applications": listdir(HOME / "Applications"),
    }


def collect(cfg):
    out = macos_items() if IS_MACOS else {}
    if shutil.which("brew"):
        out["brew_leaves"] = lines(run(["brew", "leaves"]))
        out["brew_casks"] = lines(run(["brew", "list", "--cask"]))
    code = vscode_cli()
    default = nvm_default()
    out.update({
        "vscode_extension_ids": lines(run([code, "--list-extensions"])) if code else None,
        "local_bin": listdir(HOME / ".local/bin"),
        "npm_global": listdir(NVM_VERSIONS / default / "lib/node_modules") if default else None,
    })
    return out
