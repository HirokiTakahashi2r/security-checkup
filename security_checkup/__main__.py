"""Run every collector and write results/snapshots/YYYY-MM-DD.json with changes since the previous snapshot."""

import datetime as dt
import sys

from . import config, snapshot
from .collectors import ai_tools, chrome, credentials, exposure, inventory, macos, plaintext_secrets, todo, updates

SECTIONS = [
    ("updates", updates),
    ("exposure", exposure),
    ("inventory", inventory),
    ("ai_tools", ai_tools),
    ("credentials", credentials),
    ("todo", todo),
    ("chrome_extensions", chrome),
    ("macos", macos),
    ("plaintext_secrets", plaintext_secrets),
]


def main(argv):
    if argv and argv[0] in ("-h", "--help"):
        print("usage: ./collect [YYYY-MM-DD]")
        return 0
    name = argv[0] if argv else dt.date.today().isoformat()
    dt.date.fromisoformat(name)
    cfg = config.load()
    snap = {"collected_at": dt.datetime.now().isoformat(timespec="seconds")}
    for key, module in SECTIONS:
        print(f"collecting {key} ...", flush=True)
        snap[key] = module.collect(cfg)
    out = snapshot.write(config.SNAPSHOTS, name, snap)
    summary = f" (diff from {snap['diff_from']}: {len(snap['changes'])} changes)" if "diff_from" in snap else ""
    print(f"wrote {out}{summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
