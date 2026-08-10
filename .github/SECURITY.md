# Security Policy

## Supported versions

`main` only. This project has no release train and no backport policy — fixes
land on `main` and users pull.

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

Use [GitHub Private Vulnerability Reporting](https://github.com/themarmack/research-bot/security/advisories/new)
(Security → Report a vulnerability). This keeps the report private until a fix
is ready and avoids publishing a contact email address.

This is a single-maintainer project. Realistic expectations:

- **Acknowledgement:** within 7 days.
- **Fix:** no SLA. Severity and available time decide.
- **Credit:** you will be credited in the advisory unless you ask otherwise.

## What is in scope

This repo is a collection of Claude Code *skills* — Markdown instruction files
that an AI agent reads and acts on, plus Python/shell scripts it invokes. That
makes the threat model unusual, so be specific about it.

**In scope:**

- **Malicious or subverted skill instructions.** Skills execute with the
  operator's full Claude Code permissions. A skill that instructs the agent to
  exfiltrate data, disable a guard, or run a destructive command is a
  vulnerability, not a bug.
- **Prompt-injection bypasses.** Every skill that ingests arbitrary web content
  is required to route it through
  [`prompt-injection-guard`](../.claude/skills/prompt-injection-guard/SKILL.md)
  (OWASP LLM01). A skill that fetches a URL without the guard, or an injection
  pattern the guard fails to quarantine, is in scope.
- **Credential handling.** `GMAIL_APP_PASSWORD`, `GMAIL_SEND_ADDRESS`, and
  `ANTHROPIC_API_KEY` live in `~/.config/research-bot/env` — deliberately
  outside the repo and outside any cloud-sync folder. Any code path that reads
  these into a prompt, a log, a vault note, or an outbound request is in scope.
- **Unintended writes outside the vault.** Skills are scoped to
  `~/Obsidian/Research-Brain/`. A path-traversal or an unbounded write
  elsewhere is in scope.
- **The scheduling system.** `scripts/schedule-sync.py` installs `launchd`
  agents and deploys executable scripts to
  `~/Library/Application Support/research-bot/`. Anything that lets an
  untrusted input reach those files or those plists is in scope.
- **Email delivery.** `render_and_send.py` sends vault content to a
  distribution list. Header injection, recipient injection via the Markdown
  list, or content leaking across recipients is in scope.
- **Personal data in the repo.** This is a public repo. A real email address,
  an absolute home path, or an employer name in a tracked file is a
  disclosure — `tests/test_no_pii.py` guards against it, and a bypass of that
  guard is in scope.

**Out of scope:**

- Vulnerabilities in Claude Code, the Anthropic API, Obsidian, GitHub, or
  `evolve` themselves — report those to their maintainers.
- The operator choosing to run the agent in a permissive mode. Skills cannot
  be safer than the harness permissions they are granted.
- Findings that require an attacker to already have write access to the
  operator's machine or their Obsidian vault.
- Advice quality. Skills produce research and compliance *drafts*, not
  authoritative rulings — `CLAUDE.md` requires citing sources and flagging
  uncertainty. Wrong-but-cited output is a correctness bug, not a
  vulnerability.

## Operator hardening notes

If you run this toolkit:

- Keep credentials in `~/.config/research-bot/env`. Never inline them into a
  skill, a vault note, or a prompt.
- The vault is your Tier-2 memory and is read into prompts. Do not store
  secrets, proprietary source, or internal documents there.
- Review any skill you did not write before running it — the instructions are
  the executable.
- CI here is deliberately agent-free (`.github/workflows/ci.yml` runs
  deterministic tests and static checks only, with no secrets and no API key).
  Do not add agent runs to CI against shared credentials.
