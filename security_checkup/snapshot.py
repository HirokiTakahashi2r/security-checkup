"""Write snapshots and compare them with the previous one."""

import json
import os

from .util import load_json

META = ("collected_at", "diff_from", "changes")


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}{k}."))
        return out
    return {prefix.rstrip("."): obj}


def diff(prev, cur):
    changes = {}
    fp, fc = flatten(prev), flatten(cur)
    for k in sorted(set(fp) | set(fc)):
        a, b = fp.get(k), fc.get(k)
        if a == b:
            continue
        if isinstance(a, list) and isinstance(b, list) and all(isinstance(x, str) for x in a + b):
            added, removed = sorted(set(b) - set(a)), sorted(set(a) - set(b))
            if added or removed:
                changes[k] = {"added": added, "removed": removed}
        else:
            changes[k] = {"before": a, "after": b}
    return changes


def previous(folder, name):
    earlier = sorted(p for p in folder.glob("*.json") if p.stem < name)
    return earlier[-1] if earlier else None


def write(folder, name, snap):
    folder.mkdir(parents=True, exist_ok=True)
    prev_path = previous(folder, name)
    if prev_path:
        prev = load_json(prev_path) or {}
        strip = lambda d: {k: v for k, v in d.items() if k not in META}
        snap["diff_from"] = prev_path.stem
        snap["changes"] = diff(strip(prev), strip(snap))
    out = folder / f"{name}.json"
    out.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n")
    os.chmod(out, 0o600)
    return out
