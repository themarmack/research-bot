<!--
Thanks for contributing. Keep PRs to one logical change.
Security issues go to .github/SECURITY.md, never a PR or public issue.
-->

## What and why

<!-- What changes, and what problem it solves. Link the issue if there is one. -->

Closes #

## How to verify

<!-- The commands or prompts a reviewer runs to see it working. -->

---

## Checklist

- [ ] `make check` passes (`test` + `lint` + `gate`).
- [ ] No real email addresses, absolute home paths (`/Users/...`), credentials,
      or employer names added — `tests/test_no_pii.py` enforces this.
- [ ] Commit subjects follow conventional commits (`feat:`, `fix:`, `docs:`,
      `chore:`), scoped where useful.

### If you added or changed a skill

- [ ] It lives in `.claude/skills/<name>/SKILL.md` — **not** in `skills/`
      (a symlink) and not in the global `~/.claude/skills/`.
- [ ] The `description:` contains an explicit `Use when` / `Use after` /
      `Use before` trigger phrase.
- [ ] An eval suite exists under `evals/<name>/`.
- [ ] `make evals` was run **locally** and the updated `results.*` is committed.
      *(Never run agent evals in CI.)*

### If you changed the scheduling system

Applies to `scripts/scheduled-jobs.yml`, `run-scheduled-job.sh`,
`catch-up-missed-runs.sh`, or `_catch_up_helper.py`:

- [ ] `python3 scripts/schedule-sync.py` was run in this same change.

### If you extracted logic out of a SKILL.md into a script

- [ ] Unit tests added in `tests/`, and the SKILL.md now points at the module
      so the logic lives in one tested place.

### If you touched a curated file

Applies to `voices.csv`, `skills-plan.md`, `BUILD-STEPS.md`, `CLAUDE.md`, or
`vault-template/_meta/`:

- [ ] Changes are additive — no reordering or rewriting of existing entries.
- [ ] Schema or tag-vocabulary changes were discussed in an issue first.
