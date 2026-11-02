# security-checkup

A security checkup for your macOS developer machine, reviewed together with an AI coding agent.

## How it works

1. Collect. You run `./collect`. It records what is installed, exposed and configured as a JSON snapshot. It stores names, flags and counts only. Secret values are never written.
2. Review. Your agent compares the snapshot with the previous one. It reports risky changes and recommends one fix for each. Nothing changes until you agree.
3. Record. The agent writes a dated report and updates your todo list.

The review steps are in [SKILL.md](.claude/skills/security-checkup/SKILL.md). Claude Code loads it as the `/security-checkup` skill. Codex and other agents find it through [AGENTS.md](AGENTS.md). You can also read the snapshot yourself.

## What it checks

- Pending updates
- Network exposure (firewall, listening ports)
- Newly installed things
- AI coding tools (hooks, MCP servers, permission rules)
- Credentials (static AWS keys, SSH keys without a passphrase, IAM keys)
- Todo items with due dates
- Chrome extensions
- macOS basics (FileVault, SIP, Gatekeeper, automatic updates)
- Secret-looking strings left in shell history and AI tool logs

It is built for macOS. On other systems, the macOS-specific checks are marked `unsupported` and the rest still runs.

## Quick start

You need `python3` (no extra packages) and an AI coding agent such as Claude Code or Codex.

1. Clone the repository and enable the commit checks.

   ```bash
   git clone <this repository> && cd security-checkup
   git config core.hooksPath .githooks
   ```

2. Create your private `results/` folder from the templates.

   ```bash
   mkdir -p results
   cp config.example.json results/config.json
   cp templates/private-patterns.txt templates/todo.md templates/exceptions.md results/
   ```

3. List your private values in `results/private-patterns.txt`. Examples: your username, employer and client names, cloud account IDs.

4. Open your agent in this folder and ask for a security checkup. In Claude Code, type `/security-checkup`.

5. When the agent asks, run the collector yourself.

   ```bash
   ./collect
   ```

   The collector reads SSH keys, shell history and AI tool logs to count secrets. That is why you run it, not the agent. The snapshot goes to `results/snapshots/YYYY-MM-DD.json`.

## Configuration

`results/config.json` holds settings for your machine. Every key is optional.

| Key | Meaning |
|---|---|
| `scan_roots` | Folders to search for `.claude/settings*.json` permission files |
| `ssh_key_dirs` | Folders that hold SSH private keys |
| `iam_checks` | AWS profile and IAM user pairs to list access keys for |
| `node_version_file` | A file with `node:<version>`, such as a Dockerfile, to compare your default Node with |
| `extra_secret_scans` | Named groups of file patterns to count secret-looking strings in |

## Keeping results private

- Git ignores the whole `results/` folder.
- The commit hooks block a commit that contains one of your private values or something shaped like a secret. They check the changes, file names and the commit message. They also block when `results/private-patterns.txt` is missing.
- `results/` is the only copy of your reports. Back it up, for example with Time Machine. `git clean -fdx` deletes it.

## Development

Run the tests:

```bash
python3 -m unittest discover tests
```

CI runs the tests on every push. It also fails if anything under `results/` is tracked or any file contains something shaped like a secret.

To let one line through the secret-shape check, add `pragma: allowlist secret` to it. Private values cannot be allowed this way.

```
collect                    runs the collector
security_checkup/          collector package
  __main__.py              list of checks, writes the snapshot
  config.py                results/ paths and config defaults
  secrets.py               secret patterns, redaction, commit checks
  snapshot.py              snapshot writing and diff
  collectors/              one module per check
.claude/skills/            review steps for the agent (SKILL.md)
AGENTS.md                  points Codex and other agents to SKILL.md
.githooks/                 commit hooks
.github/workflows/         CI
templates/                 starting files for results/
tests/                     unit tests
```

## License

MIT. Use at your own risk. The checkup reads sensitive places on your machine, and you decide every change it suggests.
