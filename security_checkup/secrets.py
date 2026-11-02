"""Secret patterns shared by the collectors and the git hooks.

Run as `python3 -m security_checkup.secrets --staged` (pre-commit) or
`--message FILE` (commit-msg) to block commits that contain secrets or private values,
or `--tracked` (CI) to check every tracked file for secret shapes.
"""

import re
import subprocess
import sys

from . import config

PATTERNS = {
    "aws_access_key_id": rb"AKIA[0-9A-Z]{16}",
    "aws_secret": rb"(?i)aws_secret_access_key\s*=\s*\S{20,}",
    "pg_password": rb"PGPASSWORD=[^\s'\"$]{4,}",  # pragma: allowlist secret
    "password_arg": rb"(?i)(--password=|password=|-p\s?')[^\s'\"$]{4,}",  # pragma: allowlist secret
    "openai_key": rb"sk-(proj-)?[A-Za-z0-9_-]{32,}",
    "anthropic_key": rb"sk-ant-[A-Za-z0-9_-]{20,}",
    "github_token": rb"(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,})",
    "slack_token": rb"xox[abprs]-[A-Za-z0-9-]{10,}",
    "slack_webhook": rb"hooks\.slack\.com/services/[A-Za-z0-9/]{20,}",
    "discord_webhook": rb"discord(app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]{20,}",
    "url_credentials": rb"://[^/\s:@'\"]+:[^/\s@'\"]{4,}@",
    "bearer": rb"Bearer\s+[A-Za-z0-9._~+/-]{20,}",
    "private_key": rb"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}
BYTES = {name: re.compile(p) for name, p in PATTERNS.items()}
TEXT = {name: re.compile(p.decode()) for name, p in PATTERNS.items()}
ALLOW_MARKER = "pragma: allowlist secret"


def redact(text):
    if not text:
        return text
    for name, pat in TEXT.items():
        text = pat.sub(f"<redacted:{name}>", text)
    return text


def scan_files(paths):
    counts, scanned = {}, 0
    for p in paths:
        try:
            with open(p, "rb") as f:
                for line in f:
                    scanned += len(line)
                    for name, pat in BYTES.items():
                        n = len(pat.findall(line))
                        if n:
                            counts[name] = counts.get(name, 0) + n
        except OSError:
            continue
    return {"files": len(paths), "mb": round(scanned / 1e6, 1), "counts": counts}


def load_private_patterns():
    try:
        text = config.PRIVATE_PATTERNS.read_text()
    except OSError:
        return None
    return [l.strip().lower() for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]


def find_problems(text, private):
    problems = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        hits = [f"private value #{n}" for n, p in enumerate(private, 1) if p in low]
        if ALLOW_MARKER not in line:
            hits += [name for name, pat in TEXT.items() if pat.search(line)]
        problems += [(i, h) for h in hits]
    return problems


def staged_additions():
    names = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                           capture_output=True, text=True, check=True).stdout.split()
    files = {}
    for name in names:
        diff = subprocess.run(["git", "diff", "--cached", "-U0", "--no-color", "--", name],
                              capture_output=True, text=True, check=True).stdout
        files[name] = "\n".join(l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
    return files


def tracked_files():
    names = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    files = {}
    for name in names:
        try:
            with open(name, encoding="utf-8") as f:
                files[name] = f.read()
        except (OSError, UnicodeDecodeError):
            files[name] = ""
    return files


def check(sources, require_private=True):
    private = load_private_patterns()
    if private is None and require_private:
        print(f"blocked: {config.PRIVATE_PATTERNS} is missing. Create it (see README) before committing.")
        return 1
    private = private or []
    failed = False
    for label, text in sources.items():
        if label.startswith("results/"):
            print(f"blocked: {label} is under results/, which must never be committed")
            failed = True
        for _, hit in find_problems(label, private):
            print(f"blocked: {label} (file name): {hit}")
            failed = True
        for lineno, hit in find_problems(text, private):
            print(f"blocked: {label}:{lineno}: {hit}")
            failed = True
    return 1 if failed else 0


def main(argv):
    if argv[:1] == ["--staged"]:
        return check(staged_additions())
    if argv[:1] == ["--message"] and len(argv) == 2:
        with open(argv[1]) as f:
            msg = "\n".join(l for l in f.read().splitlines() if not l.startswith("#"))
        return check({"commit message": msg})
    if argv[:1] == ["--tracked"]:
        return check(tracked_files(), require_private=False)
    print("usage: python3 -m security_checkup.secrets (--staged | --message FILE | --tracked)")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
