# Research-Bot Toolkit

A personal Claude skill toolkit for **SDLC modernization at a regulated US organization** — balancing developer innovation against elevated security and compliance demands, with GitHub Copilot / CodeQL / Dependabot operational duties on top.

This repo is **the toolkit** — both the catalog and the skill implementations. Skills live in `./.claude/skills/` inside this repo (project-scoped, versioned with the catalog), not in the user's global `~/.claude/skills/`. Long-term knowledge lives in an Obsidian vault at `~/Obsidian/Research-Brain/`.

---

## Two primary use cases

### 1. Scheduled weekly research

A growing list of cron-driven skills that run standard research prompts on a fixed cadence (daily, weekly, monthly, quarterly) and drop dated digests into the vault. Each scheduled skill answers a recurring question — "what changed in Copilot this week?", "what did the AI commentariat publish?", "what's new from financial-services regulators?" — without you having to ask.

Outputs land in `~/Obsidian/Research-Brain/digests/{cadence}/YYYY-MM-DD-{skill}.md`. The list is meant to expand: any new "what's new in X?" question you'd otherwise ask manually each week is a candidate for a scheduled skill.

Lives in **Category 2 — Scheduled / Recurring Agents** of [`skills-plan.md`](./skills-plan.md). Current entries include `weekly-intelligence-digest`, `voices-watcher`, `weekly-review`, `monthly-copilot-changelog`, `monthly-regulator-watch`, `quarterly-ai-coding-landscape`.

### 2. Ad-hoc research (Obsidian-first)

When you ask a question on demand, the skill **checks the Obsidian vault first** for prior research on the topic, then expands to the web only for confirmed gaps. New findings are added to the vault so the next ad-hoc question on the same topic builds on prior work instead of starting from scratch.

Outputs land in `~/Obsidian/Research-Brain/research/{topic}/YYYY-MM-DD-{slug}.md`. Verified facts are promoted into `vault/facts/{entity}/{predicate}.md` so subsequent questions get the answer instantly without re-research.

Lives in **Category 1 — Research (on-demand)** of [`skills-plan.md`](./skills-plan.md). Each Category 1 skill enforces the Obsidian-first contract via `vault-querier` → web fallback → `vault-writer`.

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

1. **Open the vault in Obsidian**: File → Open Vault → `~/Obsidian/Research-Brain/`. Confirm it's recognized as a vault.
2. **Read the vault conventions**: `~/Obsidian/Research-Brain/_meta/conventions.md` — describes folder layout, frontmatter schemas, tag vocabulary, and writing rules. Any skill that reads or writes the vault loads this first.
3. **Skim the catalog**: `skills-plan.md`. Pay attention to Category 0 (foundational base skills) — those are built first.
4. **Pick a skill to build**: follow the Suggested Build Order in `skills-plan.md`. Start with `source-fetcher` + `prompt-injection-guard`, then the vault read side.
5. **Use `skill-creator`** (the global meta-skill already installed at `~/.claude/skills/skill-creator/`) to scaffold each new skill — target path is `./.claude/skills/<name>/` in this repo, not the global location.

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
- Vault conventions: `~/Obsidian/Research-Brain/_meta/conventions.md` (lives in your own Obsidian vault, not this repo)
- [OB1 — Open Brain (inspiration, not dependency)](https://github.com/NateBJones-Projects/OB1)
- [jrcruciani/obsidian-memory-for-ai (vault structure source)](https://github.com/jrcruciani/obsidian-memory-for-ai)
