"""Chrome extensions per profile and whether they can read every site."""

import os
import re

from ..util import HOME, IS_MACOS, listdir, load_json, unsupported

BASE = HOME / "Library/Application Support/Google/Chrome"
ALL_SITES = ("<all_urls>", "*://*/*", "http://*/*", "https://*/*")


def ext_name(ext_dir, manifest):
    name = manifest.get("name", "")
    m = re.fullmatch(r"__MSG_(\w+)__", name)
    if not m:
        return name
    msgs = load_json(ext_dir / "_locales" / manifest.get("default_locale", "en") / "messages.json") or {}
    for k, v in msgs.items():
        if k.lower() == m.group(1).lower():
            return v.get("message", name)
    return name


def extensions(profile_dir):
    exts = []
    for ext_id in listdir(profile_dir / "Extensions") or []:
        versions = listdir(profile_dir / "Extensions" / ext_id) or []
        if not versions:
            continue
        ext_dir = profile_dir / "Extensions" / ext_id / versions[-1]
        mf = load_json(ext_dir / "manifest.json") or {}
        hosts = list(mf.get("host_permissions", [])) + [p for p in mf.get("permissions", []) if isinstance(p, str)]
        for cs in mf.get("content_scripts", []):
            hosts += cs.get("matches", [])
        exts.append({
            "id": ext_id,
            "name": ext_name(ext_dir, mf),
            "version": mf.get("version"),
            "all_sites": any(h in ALL_SITES for h in hosts),
        })
    return sorted(exts, key=lambda e: e["name"].lower())


def collect(cfg):
    if not IS_MACOS:
        return unsupported()
    try:
        profiles = [p for p in os.listdir(BASE) if p == "Default" or p.startswith("Profile ")]
    except FileNotFoundError:
        return {"not_installed": True}
    except OSError as e:
        return {"error": f"unreadable ({e.strerror})"}
    return {p: extensions(BASE / p) for p in sorted(profiles)}
