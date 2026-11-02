"""Firewall state and processes listening on every interface."""

import re
import shutil

from ..util import IS_MACOS, lines, run, tilde, unsupported
from .node import NVM_VERSIONS, nvm_default

FW = "/usr/libexec/ApplicationFirewall/socketfilterfw"
WILDCARD_HOSTS = ("*", "0.0.0.0", "[::]", "::")


def parse_fw_apps(text):
    apps, cur = [], None
    for l in (text or "").splitlines():
        m = re.match(r"\s*\d+\s*:\s*(.+?)\s*$", l)
        if m:
            cur = m.group(1)
        elif cur and "connections" in l:
            apps.append({"path": cur, "blocked": "Block" in l})
            cur = None
    return apps


def wildcard_listeners():
    if not shutil.which("lsof"):
        return None
    listen = run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"])
    found = set()
    for l in (listen or "").splitlines()[1:]:
        cols = l.split()
        if len(cols) < 9:
            continue
        host, _, _ = cols[8].rpartition(":")
        if host in WILDCARD_HOSTS:
            found.add(f"{cols[0]} {cols[8]}")
    return sorted(found)


def firewall():
    if not IS_MACOS:
        return unsupported()
    apps = parse_fw_apps(run([FW, "--listapps"]))
    default = nvm_default()
    node_path = str(NVM_VERSIONS / default / "bin/node") if default else None
    return {
        "state": run([FW, "--getglobalstate"]),
        "stealth": run([FW, "--getstealthmode"]),
        "allow_signed": lines(run([FW, "--getallowsigned"])),
        "apps": apps,
        "node_path": tilde(node_path) if node_path else None,
        "node_blocked": next((a["blocked"] for a in apps if a["path"] == node_path), None),
    }


def collect(cfg):
    return {"firewall": firewall(), "wildcard_listeners": wildcard_listeners()}
