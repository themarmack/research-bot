# Contributing

Thanks for looking. This is a single-maintainer project, but pull requests are
welcome — especially new skills, trigger-phrase fixes, and portability patches.

Start with [`README.md`](../README.md) for what the project is, and
[`CLAUDE.md`](../CLAUDE.md) for the rules AI agents follow when working in this
repo. If you use Claude Code here, it reads `CLAUDE.md` automatically.

## Setup

```bash
git clone https://github.com/themarmack/research-bot.git
cd research-bot
make setup          # venv + prod & dev deps
make check          # must pass before you open a PR
```

`make check` is the gate: `test` + `lint` + `gate`. All three are free — no API
key, no agent runs, no credentials.

## Two things that will confuse you if nobody says them

### 1. The root `skills/` symlink

`skills` at the repo root is a **tracked symlink** (git mode `120000`) pointing
at `.claude/skills/`. It exists because `evolve` hardcodes the skills path to
`<root>/skills`, while Claude Code discovers project skills from
`.claude/skills/`.

- The canonical — and only — copy of every skill is `.claude/skills/<name>/`.
- Never move the skill directories to `skills/`, never create a second real
  `skills/` tree, and never edit "the copy under `skills/`" as though it were
  separate. It is the same files.
- **Windows contributors:** run `git config --global core.symlinks true` and
  enable Developer Mode *before* cloning. Otherwise git checks the symlink out
  as a plain text file containing the path, and `evolve` silently finds zero
  skills.

Verify after cloning:

```bash
ls -l skills        # must show:  skills -> .claude/skills
```

### 2. The testing tiers are not interchangeable

Full detail in [`TESTING.md`](../TESTING.md). The short version:

| Tier | Command | Cost | Where it runs |
|------|---------|------|---------------|
| 0 — static checks | `make lint` | free | CI + local |
| 0/1 — unit + structural | `make test` | free | CI + local |
| Gate on committed evidence | `make gate` | free | CI + local |
| 1–2 — trigger + eval suites | `make evals` | **tokens** | **local / scheduled only** |

`make evals` drives the real `claude` CLI in full-auto. It is non-deterministic
and consumes tokens against whoever's credentials are present.

**Never run `evolve run triggers` or `evolve run evals` in CI.** CI gates on
*committed* results (`evolve report --check`) instead. If your change affects a
skill's behavior, run the evals locally and commit the updated `results.*`
alongside the change.

No API key is required for evals — `evolve` rides the logged-in `claude` CLI
subscription, including the LLM judge. A key only adds pre-run cost estimates.

## Adding or changing a skill

1. Scaffold with the `skill-creator` skill, and **explicitly tell it the target
   is `<repo>/.claude/skills/<name>/`** — its default is the user's global
   `~/.claude/skills/`, which is wrong for this repo. Sanity-check where the
   file landed.
2. Write the `description:` with an explicit trigger phrase — `Use when`,
   `Use after`, or `Use before`. This is enforced by `.evolve.yaml`'s
   `checks.description_pattern`. The description is how the agent decides
   whether to invoke your skill, so it matters more than the body.
   *Known backlog: ~52 existing descriptions predate this rule and are being
   burned down (issue #1). Copying their style is copying the bug.*
3. Add an eval suite under `evals/<skill>/` — see
   [`evals/README.md`](../evals/README.md).
4. Run `make evals` locally and commit the resulting `results.*`.
5. Run `make check`.

## Changing the scheduling system

If you touch any of `scripts/scheduled-jobs.yml`,
`scripts/run-scheduled-job.sh`, `scripts/catch-up-missed-runs.sh`, or
`scripts/_catch_up_helper.py`, run this **in the same change**:

```bash
python3 scripts/schedule-sync.py
```

Those files are *deployed* to `~/Library/Application Support/research-bot/` so
`launchd` can read them without `~/Documents/` access. Sync also reconciles the
`~/Library/LaunchAgents/research-bot.*.plist` files against the YAML. It is
idempotent — safe to run any time.

Note the scheduler is **macOS-only** (`launchd`). The skills themselves are
platform-neutral; only the scheduling layer is not. Portability patches for the
scheduler are welcome but should not break the macOS path.

## When you extract logic out of a skill

`CLAUDE.md` requires that prose algorithms lifted into a script get unit tests
in `tests/` in the same change, with the SKILL.md pointing at the module so the
logic lives in one tested place. `render_and_send.py` and `email_recipients.py`
are the worked examples.

Tests import the hyphenated script files by path via
[`tests/_util.py`](../tests/_util.py)'s `load_module` — the scripts are
standalone files, not an importable package.

## Never commit

- **Real email addresses.** Use `example.com` (RFC 2606). Enforced by
  `tests/test_no_pii.py`.
- **Absolute home paths** (`/Users/<you>/...`) or Claude Code project slugs
  (`-Users-<you>-...`). Use `Path.home()` or `$HOME`. Also enforced.
  *(Angle-bracket placeholders like these are explicitly allowed — that is
  what the `(?!<)` lookahead in the guard is for.)*
- **Credentials.** They belong in `~/.config/research-bot/env`, outside the
  repo. See [`SECURITY.md`](./SECURITY.md).
- **Employer names, internal docs, or proprietary code.** This toolkit is built
  for use in a regulated environment; `CLAUDE.md` treats this as a hard rule.
- **Vault content.** The Obsidian vault at `~/Obsidian/Research-Brain/` is
  personal data and is not part of this repo. Only the generic scaffold in
  `vault-template/` is tracked.

## Curated files — ask first

Append to these; do not reorder or rewrite existing rows without discussing it
in an issue: `voices.csv`, `skills-plan.md`, `BUILD-STEPS.md`, and anything in
`vault-template/_meta/`. Schema or tag-vocabulary changes want a `decisions/`
note first. See [`CODEOWNERS`](./CODEOWNERS).

## Pull requests

- One logical change per PR.
- Conventional-commit subjects (`feat:`, `fix:`, `docs:`, `chore:`), scoped
  where it helps: `fix(email-sender): ...`.
- Fill in the PR template checklist.
- `make check` must pass. CI runs the same three targets.

## Reporting bugs

Use the issue templates. For a misbehaving skill, the single most useful thing
you can include is **the exact prompt you typed** — most skill bugs are
triggering bugs, and the description is the fix.

Security issues go through [`SECURITY.md`](./SECURITY.md), not the issue
tracker.
