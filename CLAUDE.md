# CLAUDE.md — Operating rules for AI agents in this repo

See [`README.md`](./README.md) for what this project is and how it's organized. This file is **AI-specific instructions only** — rules that aren't in the README.

**Keep this file current.** When project conventions evolve — new categories, new artifacts, new "don't do that" feedback, new safety rules — update this file in the same change. If you're about to add 5+ lines here, first ask whether they belong in the README instead.

## Repo phase: catalog, not implementation

This repo is the **catalog and configuration** for the toolkit. Skill implementations live at **`./.claude/skills/<name>/SKILL.md`** — project-scoped, versioned with this repo, **not** in the user's global `~/.claude/skills/`. The only skill that lives globally is `skill-creator` (it's a meta-tool the user already has installed). Every skill we build for this toolkit goes in this repo's `.claude/skills/`.

When using `skill-creator` to scaffold a new skill, **explicitly tell it the target path is `<repo>/.claude/skills/<name>/`**, not its default global location. After creating, do a quick sanity check that the file landed in the repo, not in `~/.claude/skills/`.

The current phase is ideation; [`skills-plan.md`](./skills-plan.md) is the approved backlog. When the user says *"implement step N"* or *"run step N"*, read [`BUILD-STEPS.md`](./BUILD-STEPS.md) to find that step's skills, deps, and acceptance criteria — and execute it. Don't start implementing a skill outside that file's numbered sequence without explicit user direction.

## Skill evaluation with `evolve` — the `skills/` symlink is a bridge

The repo is wired for [`evolve`](https://oss.bitwisemedia.uk/evolve/) (a CLI that evaluates coding-agent skills). Config lives in `.evolve.yaml`; eval suites in `evals/<skill>/` (see [`evals/README.md`](./evals/README.md)).

- **`skills/` at the repo root is a symlink to `.claude/skills/`** — evolve hardcodes the skills path to `<root>/skills`, while Claude Code discovers skills from `.claude/skills/`. The canonical, only copy of every skill remains `.claude/skills/<name>/`. **Never move the skill dirs to `skills/`, never create a second real `skills/` tree, and never edit a skill "under `skills/`" as if it were separate** — it's the same files.
- **Tier discipline (regulated-env):** `evolve run checks` (Tier 0) is static, free, credential-free — safe for CI. `run triggers` / `run evals` (Tiers 1–2) drive real agent CLIs in full-auto (tokens, per-vendor credentials, non-deterministic) — run these **manually or on a schedule and commit `results.*`; do not run agents in CI.** Gate CI on committed evidence (`evolve report --check`), never by running agents on shared runners against org credentials.
- **Known backlog:** ~52 skill descriptions lack an explicit "Use when/after/before" trigger phrase (`checks.description_pattern`). These are advisory warnings (checks still exits 0), tracked as a burndown — sharpening them improves trigger accuracy.

## Testing — deterministic-first, three layers

Full detail in [`TESTING.md`](./TESTING.md). The rule: **push everything you can into the free deterministic layers; keep the AI layer thin and run it sparingly.**

- **Run it:** `make test` (Layers 0+1 — pytest, free, no AI), `make lint` (evolve Tier 0), `make gate` (`evolve report --check` on committed results), `make check` (all three = the CI gate), `make evals` (LOCAL only — drives the `claude` CLI). Deterministic tests live in `tests/` and import the hyphenated scripts by path via `tests/_util.py:load_module`.
- **No API key needed for evals** — evolve rides the logged-in `claude` CLI (subscription), including the LLM judge. A key only adds pre-run cost *estimates*.
- **CI (`.github/workflows/ci.yml`) runs Layers 0+1 + `evolve report --check` only** — zero agent tokens, no secrets. Never run `run triggers`/`run evals` in CI.
- **When you extract a prose algorithm into a script** (as `render_and_send.py` and `email_recipients.py` did), add unit tests in `tests/` in the same change, and point the SKILL.md at the module so the logic lives in one tested place.

## Memory tiers — don't duplicate

- **Tier 1**: harness auto-memory at `~/.claude/projects/<this-project>/memory/`. Identity, preferences, feedback only.
- **Tier 2**: Obsidian vault at `~/Obsidian/Research-Brain/`. Knowledge, research, facts, decisions, events, people, projects, digests.

The two never duplicate. If a candidate is factual or research-shaped, it goes to the vault; if it's about how to treat the user, it goes to Tier 1.

**Before any vault read or write**, read `~/Obsidian/Research-Brain/_meta/conventions.md` — it sets layout, frontmatter schemas, controlled tag vocabulary, and writing rules. Notes that ignore the conventions don't compose with the rest of the vault.

`vault-template/` in this repo is the **generic scaffold** that `scripts/bootstrap-vault.py` copies into a fresh vault — it exists so someone who isn't the user can bootstrap. The **live vault is authoritative** for the user's own work; the template is authoritative for what a new user gets. When you change a schema, tag, or convention, decide deliberately whether the change belongs in one or both, and never copy live vault content (which is personal data) back into the template.

## Obsidian-first contract for research

Every on-demand research task MUST query the vault first (via `vault-querier` when it exists; via filesystem grep otherwise) before doing any web research. Fall back to the web only for confirmed gaps. Write findings back to the vault so the next session benefits.

## Regulated-finance safety

The user works at a heavily regulated environment. Never:

- Paste internal repo contents, internal docs, or proprietary code into web prompts or external services.
- Name the user's employer in any prompt or written note unless the user explicitly confirms.
- Treat AI-generated content as authoritative for compliance questions — flag uncertainty and always cite sources.

## Curated artifacts — handle with care

- `voices.csv`: human-curated. Append rows or fill missing surface URLs. Do **not** auto-rewrite existing rows without confirmation; do not reorder.
- `~/Obsidian/Research-Brain/_meta/*`: curated schemas and conventions. Any schema or tag change needs a `decisions/` note first.
- The `digests/` and `research/` subfolder taxonomies (cadences and topics) are stable. Adding a new topic folder is fine; renaming or removing existing ones needs a decision note.

## Plan files vs catalog

`~/.claude/plans/*.md` are **plan-mode workspaces** — ephemeral, mode-specific scratch. The authoritative catalog is [`skills-plan.md`](./skills-plan.md). When a plan is approved, apply the changes to `skills-plan.md` (and any other affected files) in the same turn — don't leave the catalog out of sync with the approved plan.

## Scheduling system — redeploy after edits

The Category-2 scheduled skills are wired to macOS `launchd` via `scripts/scheduled-jobs.yml` and a small set of operational scripts (`run-scheduled-job.sh`, `catch-up-missed-runs.sh`, `_catch_up_helper.py`). Those operational files are **deployed** to `~/Library/Application Support/research-bot/` so launchd can read them without `~/Documents/` access (rationale in `scripts/README.md`).

**If you edit any of these files in `scripts/`, run `python3 scripts/schedule-sync.py` in the same turn**. Sync deploys the operational files AND reconciles `~/Library/LaunchAgents/research-bot.*.plist` against the yml. Idempotent — safe to run anytime.

Files whose edits require `schedule-sync.py`:
- `scheduled-jobs.yml`
- `run-scheduled-job.sh`
- `catch-up-missed-runs.sh`
- `_catch_up_helper.py`

`schedule-sync.py` and `schedule-status.py` themselves are invoked from Terminal (not launchd) and don't need redeployment.

## Email delivery — validate the distribution list before scheduled runs

The `email-sender` skill loads `~/Obsidian/Research-Brain/_config/email-distribution.md` on every invocation and parses recipients from bullet lines (plain Markdown — Obsidian-native, no YAML). Validation happens at parse time; there is no edit-time hook. A missing file, an empty list (zero bullet lines with an email), or a missing app password surfaces at the **next scheduled digest fire**, which is non-interactive. The vault write still succeeds; the email step surfaces `email_failed=<reason>` in the runner summary.

**When you edit `email-distribution.md`, validate before the next scheduled run.** Ask the user to invoke `"Show me my email distribution list"` — `email-sender.show_list` loads + parses + reports without sending. Fix any issues (empty list, malformed addresses) before the next scheduled fire.

Credentials live at `~/.config/research-bot/env` (`GMAIL_SEND_ADDRESS` + `GMAIL_APP_PASSWORD`) — same file as `ANTHROPIC_API_KEY`. Use `scripts/set-gmail-credentials.sh "you@gmail.com" "xxxx xxxx xxxx xxxx"` (with a leading space to keep it out of shell history). Never paste these into prompts or commit them. The `~/.config/` directory is outside the repo and outside any cloud-sync folder.
