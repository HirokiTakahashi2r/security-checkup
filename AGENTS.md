# Agent instructions

When asked for a security checkup, follow [.claude/skills/security-checkup/SKILL.md](.claude/skills/security-checkup/SKILL.md).

Never run `./collect` yourself, and never read SSH keys, `~/.aws`, shell history, AI tool logs, or anything else the collector scans. Ask the user to run `./collect` and read only the files SKILL.md names.
