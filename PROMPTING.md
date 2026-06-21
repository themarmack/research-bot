# Prompting Guide

Example prompts that get you to the right skill in one sentence. You don't memorize skill names — Claude Code matches your prompt against the `description:` frontmatter of every skill in `.claude/skills/` and picks the best fit. These examples show the patterns that route reliably.

Open Claude Code inside the repo directory before running any of these, so the project-scoped skills are loaded.

---

## Table of contents

1. [Scheduled work — process queued markers, force a run](#1-scheduled-work)
2. [Copilot — recurring FAQ, novel deep-dive, drafting an exception](#2-copilot--the-day-job)
3. [GHAS / GitHub / Actions — workflow hardening, IaC review, repo scoring](#3-ghas--github--actions)
4. [Vault queries — "what do we know about X?"](#4-vault-queries)
5. [Capture — quick capture, conference talk, voices roster](#5-capture)
6. [Writing artifacts — decision memo, ADR, stakeholder update, objection response](#6-writing-artifacts)
7. [Research — anything not Copilot- or GitHub-specific](#7-research--anything-else)
8. [Email — send digests + research notes via Gmail](#8-email)

Output locations at the bottom: [Where things land](#where-things-land).

---

## 1. Scheduled work

### Process today's queued markers

When the scheduling system fires a job in queue mode, it drops a marker at `~/Obsidian/Research-Brain/_inbox/scheduled-jobs/{date}-{job}.md`. You process them whenever you open Claude Code.

> **Prompt**: `Process any scheduled-job markers in the inbox.`

What happens: Claude reads `_inbox/scheduled-jobs/`, invokes each marker's named skill (e.g., `weekly-intelligence-digest`), produces the digest in the right vault folder, then deletes the marker. Markers accumulate while you're away; nothing is lost.

### Manually invoke a scheduled skill on demand

> **Prompt**: `Run the weekly-intelligence-digest skill now.`

Same prompt works for any skill in [`scripts/scheduled-jobs.yml`](./scripts/scheduled-jobs.yml). Useful when you want fresh output between scheduled runs.

### Force a scheduled-job catch-up (after the laptop was asleep)

> **Prompt**: `Check what scheduled jobs are overdue and queue catch-up markers.`

Or, equivalently, from the shell:

```bash
launchctl kickstart -k "gui/$UID/research-bot.catch-up"
```

### Status of the scheduling system

> **Prompt**: `Show me the scheduled-jobs status — next fires, last runs, exit codes.`

That invokes `scripts/schedule-status.py` and summarizes the table.

---

## 2. Copilot — the day job

### Recurring FAQ (canonical answer + compliance lens)

> **Prompt**: `Someone in legal is asking about Copilot's IP indemnity for modified suggestions. Draft a response.`

Routes to `copilot-faq-answerer`, which reads `canonical-answers.md` (vault facts override if more recent), applies the compliance lens (SR 11-7, FFIEC, etc.), and cites the source URL.

Other canonical questions that route here:

- `Where does our code go when devs use Copilot — is it used for training?`
- `What does the public code filter actually do, and is it required for the indemnity?`
- `What activity does Copilot log to the audit log?`
- `Can we pin a specific model org-wide?`

### Novel deep-dive (no canonical answer yet)

> **Prompt**: `Research the SR 11-7 model-risk implications of Copilot's agentic features (Workspace + the coding agent). Produce a research note.`

Routes to `copilot-deep-dive`. Checks the vault first (`vault/facts/copilot/**` + `vault/research/copilot/**`), then web-researches confirmed gaps via tier-1 sources, verifies load-bearing claims, and writes a research note at `vault/research/copilot/YYYY-MM-DD-{slug}.md`.

### Exception request (someone wants to deviate from policy)

> **Prompt**: `A team lead is requesting their internal sandbox repos be allowed to disable the public code filter for prompt-testing purposes. Walk me through the decision and produce the formal exception document.`

Routes to `copilot-exception-handler`. Looks up the relevant control in `vault/facts/copilot/public-code-filter.md`, walks a 7-row decision matrix, produces a `decisions/` note with risk statement, compensating controls, expiry, and renewal trigger.

### Rollout question

> **Prompt**: `We're moving from a 200-seat Copilot pilot to org-wide rollout. What's the playbook?`

Routes to `copilot-rollout-playbook`.

### Metrics analysis

> **Prompt**: `Here's the Copilot usage CSV for the past 30 days — which users are expensive vs idle, and what's the per-BU chargeback?`

Routes to `copilot-metrics-analyzer`.

---

## 3. GHAS / GitHub / Actions

### Workflow hardening

> **Prompt**: `Review .github/workflows/release.yml for hardening issues.`

Routes to `actions-workflow-hardener`. Checks against the OpenSSF Scorecard + your org's baseline (pinned actions, `permissions:` block, no `pull_request_target` with checkout-of-PR, etc.).

### Repo against the golden path

> **Prompt**: `Score this repo against our golden path — branch protections, GHAS coverage, Dependabot config, secrets-scanning, runner posture.`

Routes to `repo-golden-path-scorer`. Produces a category-weighted score with line-item findings.

### IaC security review

> **Prompt**: `Review this Terraform for security issues against CIS + our org guardrails.`

Routes to `iac-security-reviewer`. Combines checkov/tfsec semantics with the `ORG-IAC-*` rule taxonomy in the skill.

### CodeQL onboarding

> **Prompt**: `Given this Java + Python repo with PCI-relevant flows, recommend a CodeQL setup: default vs advanced, query suite, custom packs.`

Routes to `codeql-onboarding-helper`.

### GHAS config review

> **Prompt**: `Audit this repo's GHAS configuration — Dependabot, code scanning, secret scanning, custom patterns.`

Routes to `ghas-config-reviewer`.

### Dependabot config

> **Prompt**: `Draft a dependabot.yml for this repo (Node + Python + Docker).`

Routes to `dependabot-config-helper`.

### Audit-log investigation

> **Prompt**: `Pull the org audit log for the last 7 days and surface anomalous admin actions (new org admins, OAuth grants, IP allow-list edits).`

Routes to `enterprise-audit-log-investigator`.

---

## 4. Vault queries

The vault accumulates facts, research, decisions, events, people, projects, and digests. When you ask a question, the matching skill checks the vault first.

### "What do we know about X?"

> **Prompt**: `What do we know about Copilot content exclusion at the repo level?`

Routes to `vault-querier`. Returns matching `facts/copilot/`, `research/copilot/`, `digests/`, with paths + source URLs + `last_verified` dates.

### Facts vs research vs digests

> **Prompt**: `Show me every fact note in vault/facts/copilot/ with last_verified older than 90 days.`

Routes to `vault-querier`.

---

## 5. Capture

### Quick capture (perishable context)

> **Prompt**: `Quick capture: legal asked in today's standup about IP indemnity coverage for code that was AI-suggested but then heavily modified by the dev. They want a written response by Friday.`

Routes to `quick-capture`. Produces a structured `_inbox/` note with type=decision-pending or meeting-note, suggested promote path, and a follow-up tag.

### Conference talk → structured note

> **Prompt**: `I watched the GitHub Universe talk "Beyond the Prompt: Agentic SDLC at Scale". Pull out the structured findings.`

Routes to `conference-talk-distiller`. Output goes to `vault/research/conference/`.

### Add a person to the voices roster

> **Prompt**: `Add @newvoice (LinkedIn URL: ..., focus: AI governance) to voices.csv.`

Routes to `voices-roster-curator`. Appends a row with the enriched bio + role + surface URLs.

### Learning capture (after a deep dive)

> **Prompt**: `Capture what I learned from the OCC RFI deep-dive as a learning note.`

Routes to `learning-capture`. Produces a `vault/insights/{slug}.md` linking back to the source research.

---

## 6. Writing artifacts

### Decision memo

> **Prompt**: `Write a decision memo for whether to enable the Copilot coding agent for the Java teams. Pull options, risks, and recommendation from vault facts.`

Routes to `decision-memo-writer`. Output goes to `vault/decisions/YYYY-MM-DD-{slug}.md`.

### ADR

> **Prompt**: `Write an ADR for our choice to use GitHub-hosted runners with the hardened-codeql group instead of self-hosted runners for the CodeQL workflow.`

Routes to `adr-writer`.

### Stakeholder update

> **Prompt**: `Draft this month's Copilot stakeholder update — usage, savings, risk posture, what's next. Pull from the metrics analyzer output and recent digests.`

Routes to `stakeholder-update-writer`.

### Objection response

> **Prompt**: `Audit just raised: "We can't trace which Copilot suggestion ended up in which commit. SOX-relevant?" Give me a calibrated response.`

Routes to `objection-response-library`. Reads the canonical entry, applies the steel-manned concern → response → citation → what's-NOT-covered → escalation structure.

### RFC

> **Prompt**: `Write an RFC proposing a new control: require AGENTS.md governance review for any repo using Copilot's coding agent.`

Routes to `rfc-writer`.

---

## 7. Research — anything else

### Financial-services regulators

> **Prompt**: `What did the OCC publish this month on AI in banking? Tie findings to control-catalog mappings.`

Routes to `financial-regulator-watch`.

### AI governance frameworks

> **Prompt**: `Compare NIST AI RMF profile guidance for SDLC vs the EU AI Act's high-risk classification criteria.`

Routes to `ai-governance-research`.

### Peer-bank intel

> **Prompt**: `What have Goldman, JPM, and Capital One publicly said about AI coding tools in the last 6 months?`

Routes to `peer-bank-tech-intel`.

### Frontier model watch

> **Prompt**: `New Anthropic Opus 4.8 — what's the model card say about coding eval performance, and does anything in it affect what Copilot will route to for our org?`

Routes to `frontier-model-watch`.

### Incident postmortem research

> **Prompt**: `Research the Cloudflare 2024-XX outage — what's the SDLC lesson, and does it apply to our deployment pipeline?`

Routes to `incident-postmortem-research`.

### Vendor security eval

> **Prompt**: `Evaluate <vendor> against our policy: data flow, SIG/SOC 2, model training opt-out, breach history.`

Routes to `vendor-security-eval`.

### Generalist SDLC question

> **Prompt**: `What's current state of feature-flag governance for regulated apps?`

Routes to `sdlc-best-practice`.

---

## 8. Email

Send digests + research notes via Gmail SMTP. Requires one-time setup (see README §"Email delivery (optional)"): an app password in `~/.config/research-bot/env` and a `~/Obsidian/Research-Brain/_config/email-lists.yml` configured from the [template](./.claude/skills/email-sender/recipients.example.yml).

### Ask-and-send after a research note writes

> **Prompt**: `Research SR 11-7 implications for the Copilot coding agent and email me the result.`

The Category 1 researcher (`copilot-deep-dive` in this case) writes the note to `vault/research/copilot/`, then `email-sender.prompt_then_send` asks you which list to deliver to ("leadership / team / self / skip"). You pick; the email goes; the vault note remains. If you just asked for research without "email me," Claude still offers — research notes always ask after the write.

### Force-send an existing digest

> **Prompt**: `Email the most recent weekly-intelligence-digest to leadership.`

Routes directly to `email-sender.send_to_list`. The path is resolved from `vault/digests/weekly/{latest}-weekly-intelligence-digest.md`. Useful when (a) auto-send was disabled in `digest_routing`, (b) you want a re-send, or (c) you're sending to a different list than the routed default.

### List the configured lists + routing map

> **Prompt**: `What email lists do I have and which digests auto-send where?`

Loads `email-lists.yml`, validates it, and prints the lists + their recipients + the `digest_routing` map. Useful before adding a new digest or changing audiences. If the config is missing or malformed, surfaces the exact stop-and-report message with remediation.

### Troubleshoot a misconfig

> **Prompt**: `My scheduled digest didn't email this morning — what broke?`

Reads the relevant per-job log under `~/Library/Logs/research-bot/` for the failure line (`email_failed=<reason>`), then translates the error into the likely fix: regenerate the app password, fix YAML syntax, add missing recipient, etc. Common cases:

- `email_failed=config missing` → `~/Obsidian/Research-Brain/_config/email-lists.yml` not present.
- `email_failed=GMAIL_APP_PASSWORD not set` → env file missing the var.
- `email_failed=SMTP auth failed` → app password expired or revoked; regenerate at https://myaccount.google.com/apppasswords.
- `email_failed=unknown list 'X'` → typo in `digest_routing`.

The digest itself still lands in the vault even when email fails — email is a delivery channel, not a write-blocker.

---

## Where things land

| Artifact | Path | Skill that writes it |
|----------|------|----------------------|
| Scheduled-job marker | `vault/_inbox/scheduled-jobs/{date}-{job}.md` | `run-scheduled-job.sh` |
| Daily / weekly / monthly / quarterly digest | `vault/digests/{cadence}/YYYY-MM-DD-{skill}.md` | scheduled Category 2 skills via `digest-writer` |
| Ad-hoc research note | `vault/research/{topic}/YYYY-MM-DD-{slug}.md` | Category 1 skills via `vault-writer.write_research` |
| Verified fact | `vault/facts/{entity}/{predicate}.md` | `vault-writer.write_fact` (promoted from `_inbox/` by `memory-curator`) |
| Decision (incl. exceptions) | `vault/decisions/YYYY-MM-DD-{slug}.md` | decision-writing skills |
| Insight / learning capture | `vault/insights/{slug}.md` | `learning-capture` |
| Person note | `vault/people/{handle}.md` | `voices-roster-curator`, quick capture |
| Quick-capture entry | `vault/_inbox/quick-capture/{ts}-{slug}.md` | `quick-capture` (sweep promotes later) |
| Tier-1 harness memory | `~/.claude/projects/<this-project>/memory/*.md` | Claude Code harness (auto) |
| Email recipient lists | `~/Obsidian/Research-Brain/_config/email-lists.yml` | hand-curated (template in `.claude/skills/email-sender/`) |
| Gmail credentials | `~/.config/research-bot/env` (`GMAIL_SEND_ADDRESS`, `GMAIL_APP_PASSWORD`) | hand-curated; sourced by scheduled-job wrapper and email-sender |

---

## How skill matching works (one paragraph)

Each `.claude/skills/<name>/SKILL.md` starts with a `description:` field that Claude Code reads. When you prompt, the harness scores your message against every description and routes to the highest match. The descriptions are written to be **disambiguating** — a Copilot question matches `copilot-faq-answerer` or `copilot-deep-dive` (not `github-platform-watch`), a workflow-file review matches `actions-workflow-hardener` (not the broader `secure-design-reviewer`). If two skills could plausibly fit, Claude asks you which intent you meant before proceeding.

If you're not sure what skill exists for a thing, the catalog in [`skills-plan.md`](./skills-plan.md) groups all ~60 skills by category. Or just describe the thing — if no skill matches, Claude will tell you it's a gap.
