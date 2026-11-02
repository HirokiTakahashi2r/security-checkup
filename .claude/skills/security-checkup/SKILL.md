---
name: security-checkup
description: Run a security checkup of this machine. Triggered by "security checkup", "run the checkup", "セキュリティ点検して" and similar. Compares the collected snapshot with the previous one, reports risky changes with a recommended fix, applies only the fixes the user agrees to, and records the result in results/YYYY-MM-DD.md.
---

# Security checkup

Run from the repository root. All personal data lives in `results/`, which is gitignored.

## 1. Collect

The user runs the collector. The agent does not run it, because it reads SSH keys, shell history and AI tool logs.

```
./collect
```

In Claude Code the user can type `! ./collect` so the output lands in the conversation.

If `results/config.json` lists `iam_checks`, the user must be logged in to those AWS profiles first (for example `aws sso login --profile <profile>`). Otherwise IAM keys are recorded as `unverified`.

The output is `results/snapshots/YYYY-MM-DD.json`. It holds names, flags and counts only, never secret values. Read only this JSON, `results/todo.md`, `results/exceptions.md` and the previous report. Never read SSH keys, `~/.aws`, shell history, AI tool logs, or anything listed in `extra_secret_scans`.

## 2. Judge

If the snapshot has `changes`, focus on them. For the first run, or categories without changes, judge the current state with the table below. Do not report anything listed in `results/exceptions.md`. When the user decides to keep something, add it there with the reason.

A change from `unverified` (or `null`) to a real value is not a finding.

| Category | JSON key | Report when |
|---|---|---|
| Updates | `updates` | `macos_updates` or `brew_outdated` is not empty. More than one `node_versions`. `node_default` differs from `node_expected` |
| Exposure | `exposure` | Firewall disabled. `node_blocked` is false or null (re-register after a Node upgrade). New entries in `wildcard_listeners`. New allowed entries in `firewall.apps` |
| Inventory | `inventory` | Anything new in launchd jobs, privileged helpers, apps, brew, VS Code extensions, `~/.local/bin`, or global npm. Ask whether the user installed it. Look harder at VS Code extensions from individual publishers |
| AI tools | `ai_tools` | New hooks or statusLine, new MCP servers or Codex trusted projects, non-empty `broad` permissions, a large jump in `allow` counts, non-empty `system_python_user_packages` or `default_python_packages` |
| Credentials | `credentials` | `aws_static_keys` is not 0. Any `passphrase: false`. New keys. Any `Active` IAM key |
| Todo | `todo` | `overdue` and `due_within_7_days` |
| Chrome extensions | `chrome_extensions` | New extensions, or `all_sites: true`. On `error`, macOS privacy protection blocked the read: ask the user to open `chrome://extensions` and tell you what is installed |
| macOS basics | `macos` | FileVault, SIP or Gatekeeper disabled. Any automatic update setting that is not `1` |
| Plaintext secrets | `plaintext_secrets` | `counts` grew since the previous snapshot, or anything in `claude_settings`. Say which group of files, never the values |

Sections marked `unsupported` do not apply to this OS. Skip them.

## 3. Report and agree

Report in the conversation, in the user's language.

- For each finding: what is happening, why it is risky, and one recommended fix.
- Problems unchanged since the previous report get one line, without repeating the explanation.
- Apply nothing until the user chooses. Do not start deleting or changing settings in the same message as the report.

## 4. Apply

- Delete by moving to the Trash (`~/.Trash/<what>-removed-YYYYMMDD`), not `rm`.
- Before editing a settings file, copy it to `<file>.bak.YYYYMMDD`. Keep backups that contain secrets in a folder with permission 700.
- For anything needing sudo, show the command and let the user run it in their own terminal. Password prompts may not work through `!`.
- `socketfilterfw` prints nothing when it fails. After changing the firewall, always confirm with `--getappblocked` or similar.
- After each fix, re-check the item with a read-only command.

## 5. Record

Write `results/YYYY-MM-DD.md` (the checkup date) in the user's language, following `templates/report.md`. The previous report is the latest `results/*.md` dated before today.

Then update `results/todo.md`: remove finished items and record them in the report; add follow-up work with a due date.

## Writing rules

- Never write secret values, access key IDs or passwords in reports or in the conversation.
