"""Static AWS keys, SSH private keys without a passphrase, and IAM access key status."""

import json
import re
import subprocess

from ..util import HOME, expand, listdir, read_text, run, tilde

SKIP_PREFIXES = ("config", "known_hosts", "authorized_keys")


def has_passphrase(path):
    try:
        r = subprocess.run(["ssh-keygen", "-y", "-P", "", "-f", str(path)], capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.returncode != 0


def ssh_keys(dirs):
    keys = {}
    for d in map(expand, dirs):
        for n in listdir(d) or []:
            p = d / n
            if not p.is_file() or n.endswith(".pub") or n.startswith(SKIP_PREFIXES):
                continue
            try:
                head = p.read_bytes()[:64]
            except OSError:
                continue
            if b"PRIVATE KEY" in head:
                keys[tilde(p)] = {"passphrase": has_passphrase(p)}
    return keys


def iam_keys(checks):
    out = {}
    for c in checks:
        res = run(["aws", "iam", "list-access-keys", "--user-name", c["user"], "--profile", c["profile"],
                   "--query", "AccessKeyMetadata[].[Status,CreateDate]", "--output", "json"], timeout=30)
        out[f"{c['profile']}/{c['user']}"] = json.loads(res) if res else "unverified"
    return out


def collect(cfg):
    cred = read_text(HOME / ".aws/credentials") or ""
    return {
        "aws_static_keys": len(re.findall(r"^\s*aws_access_key_id\s*=", cred, re.M)),
        "ssh_private_keys": ssh_keys(cfg["ssh_key_dirs"]),
        "iam_access_keys": iam_keys(cfg["iam_checks"]),
    }
