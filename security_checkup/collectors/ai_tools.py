"""Claude Code and Codex hooks, MCP servers, permission rules, and stray Python packages."""

import os
import re
from pathlib import Path

from ..secrets import redact
from ..util import HOME, IS_MACOS, expand, lines, load_json, read_text, run, tilde

BROAD_RULE = re.compile(
    r"Bash\((rm|curl|wget|ssh|scp|rsync|aws|sudo|python3?|node|npx|bash|sh|zsh|eval|docker|psql|"
    r"git|git push|git reset|git checkout|gh|kill|chmod|mv|cp|npm|pnpm|yarn|pip3?|uv|env|xargs|"
    r"perl|ruby|sed|awk|find|export|for|cd|terraform|kubectl|brew|launchctl|tee|tar|open|osascript)"
    r"(:\*| \*|\*)\)"
)
SKIP_DIRS = ("node_modules", ".git", ".venv", "venv")


def hook_commands(settings):
    out = []
    for event, groups in ((settings or {}).get("hooks") or {}).items():
        for g in groups:
            for h in g.get("hooks", []):
                out.append(f"{event}: {redact(h.get('command', ''))[:120]}")
    return sorted(out)


def permission_files(cfg):
    files = [HOME / ".claude/settings.json", HOME / ".claude/settings.local.json"]
    for root in cfg["scan_roots"]:
        for dirpath, dirs, names in os.walk(expand(root)):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            if dirpath.endswith("/.claude"):
                files += [Path(dirpath) / n for n in names if n in ("settings.json", "settings.local.json")]
    return files


def permissions(cfg):
    out = {}
    for p in permission_files(cfg):
        perms = (load_json(p) or {}).get("permissions") or {}
        allow = perms.get("allow") or []
        out[tilde(p)] = {
            "allow": len(allow),
            "deny": len(perms.get("deny") or []),
            "broad": sorted(r for r in allow if BROAD_RULE.fullmatch(r)),
        }
    return out


def collect(cfg):
    claude = load_json(HOME / ".claude/settings.json") or {}
    claude_json = load_json(HOME / ".claude.json") or {}
    mcp = {"global": sorted((claude_json.get("mcpServers") or {}).keys())}
    for proj, v in (claude_json.get("projects") or {}).items():
        if v.get("mcpServers"):
            mcp[tilde(proj)] = sorted(v["mcpServers"].keys())
    plugins = load_json(HOME / ".claude/plugins/installed_plugins.json") or {}
    codex_toml = read_text(HOME / ".codex/config.toml") or ""
    default_py = run(["python3", "-m", "pip", "list", "--format=freeze"])
    out = {
        "claude_hooks": hook_commands(claude),
        "claude_statusline": redact((claude.get("statusLine") or {}).get("command", ""))[:120] or None,
        "claude_plugins": sorted((plugins.get("plugins") or plugins).keys()) if isinstance(plugins, dict) else [],
        "claude_mcp": mcp,
        "codex_hooks": hook_commands(load_json(HOME / ".codex/hooks.json")),
        "codex_mcp_servers": sorted(set(re.findall(r"^\[mcp_servers\.([^\]]+)\]", codex_toml, re.M))),
        "codex_trusted_projects": sorted(tilde(p) for p in set(re.findall(r'^\[projects\."([^"]+)"\]', codex_toml, re.M))),
        "permissions": permissions(cfg),
        "default_python_packages": [p for p in lines(default_py) if not p.startswith(("pip==", "setuptools=="))],
    }
    if IS_MACOS:
        out["system_python_user_packages"] = lines(run(["/usr/bin/python3", "-m", "pip", "list", "--user", "--format=freeze"]))
    return out
