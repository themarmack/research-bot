# Research-Bot Toolkit

A personal Claude skill toolkit for **SDLC modernization at a regulated US organization** — balancing developer innovation against elevated security and compliance demands, with GitHub Copilot / CodeQL / Dependabot operational duties on top.

This repo is **the toolkit** — both the catalog and the skill implementations. Skills live in `./.claude/skills/` inside this repo (project-scoped, versioned with the catalog), not in the user's global `~/.claude/skills/`. Long-term knowledge lives in an Obsidian vault at `~/Obsidian/Research-Brain/`.

---

## Two primary use cases

### 1. Scheduled weekly research

A growing list of cron-driven skills that run standard research prompts on a fixed cadence (daily, weekly, monthly, quarterly) and drop dated digests into the vault. Each scheduled skill answers a recurring question — "what changed in Copilot this week?", "what did the AI commentariat publish?", "what's new from financial-services regulators?" — without you having to ask.

Outputs land in `~/Obsidian/Research-Brain/digests/{cadence}/YYYY-MM-DD-{skill}.md`. The list is meant to expand: any new "what's new in X?" question you'd otherwise ask manually each week is a candidate for a scheduled skill.

Lives in **Category 2 — Scheduled / Recurring Agents** of [`skills-plan.md`](./skills-plan.md). The 9 currently wired jobs:

| Job | Cadence | What it answers |
|-----|---------|-----------------|
| `voices-watcher` | daily 07:30 | What did the AI/product commentariat publish? |
| `daily-cve-digest` | weekdays 07:00 | Any new CVEs in our stack today? |
| `weekly-intelligence-digest` | Mon 07:00 | What changed across all my watched sources this week? |
| `weekly-review` | Sun 18:00 | What did I learn / decide / open this week? |
| `biweekly-codeql-community-pulse` | every other Tue 08:00 | New CodeQL queries, packs, talks? |
| `monthly-copilot-changelog` | 1st 07:00 | What shipped in Copilot this month? |
| `monthly-regulator-watch` | 1st 08:00 | What's new from financial-services regulators? |
| `conference-cfp-and-recap-watch` | 15th 09:00 | Conference CFPs opening or recaps to digest? |
| `quarterly-ai-coding-landscape` | Jan/Apr/Jul/Oct 1st 09:00 | State of the AI-coding market this quarter? |

**Install / sync (one-time, after cloning):**

```bash
cd <repo>
python3 -m pip install -r scripts/requirements.txt
python3 scripts/schedule-sync.py
```

That generates one `~/Library/LaunchAgents/research-bot.{job}.plist` per job (plus a catch-up agent that runs at login and hourly) and copies the operational scripts to a TCC-unprotected location so launchd can read them without any permission grant. Edit `scripts/scheduled-jobs.yml` and re-run sync any time to add/remove/change jobs — it's idempotent.

**Default mode: queue (zero API cost at fire time).** When a job's scheduled time hits, the wrapper writes a marker to `~/Obsidian/Research-Brain/_inbox/scheduled-jobs/{date}-{job}.md`. You process the marker by opening Claude Code and asking it to run the skill (see [`PROMPTING.md`](./PROMPTING.md) §1). Markers accumulate while you're away; nothing is lost.

Deep detail (architecture diagram, claude-headless mode, troubleshooting): [`scripts/README.md`](./scripts/README.md).

#### Email delivery (optional)

Scheduled digests auto-email to everyone on a single distribution list; ad-hoc research notes prompt `[y/n]` before sending. Uses Gmail SMTP — no OAuth setup. The recipient list is a plain Markdown note in your Obsidian vault, so you manage it the same way you manage any other note.

One-time setup:

1. **Enable 2-Step Verification** on the Google account you'll send from (required for app passwords).
2. **Generate an app password** at https://myaccount.google.com/apppasswords ("Mail" → "Other / research-bot"). Google shows a 16-character password once — copy it.
3. **Store the credentials** (writes to `~/.config/research-bot/env`, the same file that already holds `ANTHROPIC_API_KEY`):
   ```bash
   # Note the leading space — keeps the command out of shell history on macOS zsh.
    scripts/set-gmail-credentials.sh "you@gmail.com" "xxxx xxxx xxxx xxxx"
   ```
4. **Create your distribution list** in the vault:
   ```bash
   mkdir -p ~/Obsidian/Research-Brain/_config
   cp .claude/skills/email-sender/email-distribution.example.md \
      ~/Obsidian/Research-Brain/_config/email-distribution.md
   # Open it in Obsidian. Edit the "## Recipients" bullets. Save.
   ```
5. **Verify**: ask Claude Code `"Show me my email distribution list"` to confirm parsing, then `"Email the most recent weekly-intelligence-digest as a test"` for a real SMTP round-trip.

After setup, scheduled digests fire-and-forget to everyone on the list. Research notes always prompt first. Misconfig (missing env var, missing distribution file, empty list, SMTP auth failure) stop-and-reports with the exact remediation — no silent drops, no half-sends.

The list lives in your vault (Obsidian-editable, not in this public repo). Pause a recipient by wrapping the bullet in `<!-- ... -->` — no deletion needed. Skill: [`email-sender`](./.claude/skills/email-sender/SKILL.md). Prompting examples: [`PROMPTING.md`](./PROMPTING.md) §Email.

### 2. Ad-hoc research (Obsidian-first)

When you ask a question on demand, the skill **checks the Obsidian vault first** for prior research on the topic, then expands to the web only for confirmed gaps. New findings are added to the vault so the next ad-hoc question on the same topic builds on prior work instead of starting from scratch.

Outputs land in `~/Obsidian/Research-Brain/research/{topic}/YYYY-MM-DD-{slug}.md`. Verified facts are promoted into `vault/facts/{entity}/{predicate}.md` so subsequent questions get the answer instantly without re-research.

Lives in **Category 1 — Research (on-demand)** of [`skills-plan.md`](./skills-plan.md). Each Category 1 skill enforces the Obsidian-first contract via `vault-querier` → web fallback → `vault-writer`.

You don't memorize skill names — just describe what you want. See [`PROMPTING.md`](./PROMPTING.md) for example prompts that get you to the right skill in one sentence.

#### Executive summaries (optional)

`executive-summary-writer` turns a research note into a 1-page exec summary, personalized per audience. Length, voice, format, and emphasis are tuned by reading `~/Obsidian/Research-Brain/_config/exec-preferences.md` — a Markdown doc where each H2 (`## CISO`, `## VP Engineering`, etc.) defines one audience. A required `## Default` section is the fallback for unspecified audiences and the field-by-field backstop for named ones.

The summary follows an 8-section spine: BLUF, Why This Matters Now, Key Findings, Implications, Recommended Action, Risks, Next Decision Point, Sources. Three sections are mandatory; the other five can be toggled per audience. Output lands at `vault/insights/YYYY-MM-DD-exec-summary-{audience}-{slug}.md` and prompts to email afterward via `email-sender`.

One-time setup:

```bash
mkdir -p ~/Obsidian/Research-Brain/_config
cp .claude/skills/executive-summary-writer/exec-preferences.example.md \
   ~/Obsidian/Research-Brain/_config/exec-preferences.md
# Open it in Obsidian. Edit the ## Default section + any named audiences (## CISO, etc.). Save.
```

After setup, try `"summarize the latest Copilot research for the CISO"` — the skill loads prefs, generates a CISO-tuned 1-pager, writes to `insights/`, and asks if you want to email it. Validate the prefs file any time with `"list my executive audiences"` ([`PROMPTING.md`](./PROMPTING.md) §9). Skill: [`executive-summary-writer`](./.claude/skills/executive-summary-writer/SKILL.md).

---

## Architecture (one paragraph)

Two-tier memory: **Tier 1** is the Claude Code harness's auto-memory at `~/.claude/projects/<this-project>/memory/` (narrow, auto-loaded, identity + preferences + feedback). **Tier 2** is the Obsidian vault at `~/Obsidian/Research-Brain/` (broad, queried on demand, knowledge + research + facts + decisions + events + people + projects + digests). A `memory-curator` skill decides which tier gets each candidate. Structure follows `jrcruciani/obsidian-memory-for-ai` v3.1 conventions, with prompt patterns borrowed from Nate Jones's [OB1](https://github.com/NateBJones-Projects/OB1) — specifically the Quick Capture templates, the Weekly Review structure, and two writing rules ("self-contained" + "stop and report"). OB1's self-hosted DB / gateway / MCP infrastructure is **not** used — this toolkit stays plain Markdown so the vault is portable and the system is one person's tool, not a platform.

## Layout

| Path | What |
|------|------|
| `./skills-plan.md` | Full catalog: ~60 skills across 6 categories + Category 0 Foundational Base Skills + Memory Architecture |
| `./voices.csv` | AI/product-strategy commentariat roster (seed from @natebjones's Following list); read by `voices-watcher` and `voices-roster-curator` |
| `./README.md` | This file |
| `~/Obsidian/Research-Brain/` | The Tier-2 vault (separate from this repo). Start at `_meta/conventions.md`. |
| `./.claude/skills/` | Skill implementations (74 built across Phase 1 + Phase 2) |
| `./scripts/` | Scheduling system (`launchd` plist sync + queue-mode wrappers) |
| `./BUILD-STEPS.md` | Stepwise build history (~34 numbered steps) |
| `~/.claude/projects/<this-project>/memory/` | Tier-1 harness auto-memory |

## Getting started

1. **Clone the repo** somewhere readable from your shell. The skills are project-scoped — Claude Code picks them up automatically when you run inside the repo.
2. **Set up the Obsidian vault** at `~/Obsidian/Research-Brain/` following `_meta/conventions.md`. The vault is not part of this repo (it's where outputs land); use the schemas in `_meta/schema/*.yml` to scaffold it. Most Category 1/2 skills will fail loudly if the vault structure isn't there.
3. **Install the scheduling system** (optional but recommended):
   ```bash
   cd <repo>
   python3 -m pip install -r scripts/requirements.txt
   python3 scripts/schedule-sync.py
   ```
   That installs 9 launchd agents + a catch-up agent. See [`scripts/README.md`](./scripts/README.md) for what gets created.
4. **Open Claude Code in the repo directory** and try a prompt from [`PROMPTING.md`](./PROMPTING.md). Example: `"What do we know about Copilot's IP indemnity?"` will route to `copilot-faq-answerer`, which checks vault facts before answering.
5. **Tier-1 memory bootstrap** (optional): Claude Code maintains harness memory at `~/.claude/projects/<this-project>/memory/`. You can pre-seed it with `user_role.md` / `user_preferences.md` files describing your context — those auto-load in every conversation.

## Status

- **Catalog**: approved (~60 skills, 6 categories + Memory layer).
- **Vault scaffold**: built at `~/Obsidian/Research-Brain/` (conventions, schemas, templates).
- **Voices roster**: seeded with 38 handles in `voices.csv`.
- **Skill implementations**: 74 built across Phase 1 + Phase 2. See [`BUILD-STEPS.md`](./BUILD-STEPS.md) for the stepwise build history.
- **Scheduling**: 9 scheduled skills wired to macOS `launchd` via `scripts/schedule-sync.py` (queue mode by default — see [`scripts/README.md`](./scripts/README.md)).
- **OB1 inspiration**: borrowed Quick Capture templates, Weekly Review structure, two writing rules. Skipped OB1's self-hosted infrastructure.

## Design lenses (from OB1's Spark patterns)

When considering a new skill, classify it against these five workflow patterns. Most strong candidates fit at least one:

- **Save This** — preserve AI-generated insights (Category 6: `learning-capture`, `quick-capture`)
- **Before I Forget** — capture perishable context (Category 6: `quick-capture` decision/meeting templates)
- **Cross-Pollinate** — search across tools (Category 1: every on-demand researcher; the Obsidian-first contract is the canonical implementation)
- **Build the Thread** — accumulate insight over time (Category 2: scheduled digests writing to the vault; the durable `facts/` and `insights/` folders)
- **People Context** — remember what matters about people (`voices.csv` + `vault/people/` + `voices-roster-curator`)

## References

- [Skills catalog](./skills-plan.md)
- [Prompting guide](./PROMPTING.md) — example prompts by use case
- [Scheduling system deep detail](./scripts/README.md) — install, claude-headless mode, troubleshooting
- Vault conventions: `~/Obsidian/Research-Brain/_meta/conventions.md` (lives in your own Obsidian vault, not this repo)
- [OB1 — Open Brain (inspiration, not dependency)](https://github.com/NateBJones-Projects/OB1)
- [jrcruciani/obsidian-memory-for-ai (vault structure source)](https://github.com/jrcruciani/obsidian-memory-for-ai)
