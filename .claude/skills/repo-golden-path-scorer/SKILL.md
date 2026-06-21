---
name: repo-golden-path-scorer
description: Score a repo against the org's golden-path standards — CODEOWNERS, branch protection, required checks, signed commits, dependabot.yml currency, SECURITY.md, AGENTS.md, code-scanning enabled, secret scanning + push protection, license declared, README/CONTRIBUTING basics. Produces a 100-point scorecard with category subtotals and prioritized remediation. Use during repo onboarding, periodic sweeps of high-blast-radius repos, before a stakeholder review where you need a posture summary, or as the basis for an org-wide consistency report.
---

# repo-golden-path-scorer

A Category 3 ops tool. The org's "golden path" is the set of repo-level standards every production repo should meet. This skill makes the assessment reproducible: same checks every time, same weighting, structured output.

## When to use

- Repo onboarding — score before / after to confirm baseline met.
- Periodic sweep of high-blast-radius repos (regulated data, customer-facing, financial-reporting).
- Posture summary for a stakeholder review.
- Org-wide consistency report — score N repos, surface bottom quartile.

## When NOT to use

- Strategic decisions about which standards to adopt → that's a `decisions/` note.
- GHAS-specific deep audit → `ghas-config-reviewer`.
- Org-level settings → `github-org-audit-runner`.

## Scoring rubric (100 points total)

| Category | Points | Items |
|----------|--------|-------|
| Ownership + review | 20 | CODEOWNERS exists (5); covers all important paths (5); branch protection requires CODEOWNERS review (5); required reviewers ≥1 (5) |
| Branch protection | 15 | Protected default branch (5); requires PR (5); requires status checks (5) |
| Code scanning | 15 | CodeQL enabled (5); required to pass for merge (5); using `security-extended` or higher (5) |
| Secret scanning | 10 | Enabled (5); push protection enabled (5) |
| Dependabot | 15 | `dependabot.yml` exists (5); covers all declared ecosystems (5); follows org pattern per [[2026-06-20-dependabot-best-practices-regulated-org]] (5) |
| Repo metadata | 10 | README present (2); CONTRIBUTING present (2); SECURITY.md present (3); LICENSE present (3) |
| Copilot governance | 10 | `AGENTS.md` present (5); references org policy (5) |
| Hygiene | 5 | No long-lived secrets in workflow (5) |

**Total**: 100. **Pass threshold**: 80. **Excellent**: 95+.

## Workflow

1. **Identify repo** (the user provides `owner/repo`).
2. **Inspect via `gh api` + repo content fetches**:
   - `gh api repos/{owner}/{repo}/contents/CODEOWNERS`
   - `gh api repos/{owner}/{repo}/branches/{default}/protection`
   - `gh api repos/{owner}/{repo}/code-scanning/default-setup`
   - `gh api repos/{owner}/{repo}/secret-scanning/alerts` (existence implies enabled)
   - `gh api repos/{owner}/{repo}/contents/.github/dependabot.yml`
   - `gh api repos/{owner}/{repo}/contents/README.md` / `CONTRIBUTING.md` / `SECURITY.md` / `LICENSE`
   - `gh api repos/{owner}/{repo}/contents/AGENTS.md` (and `.github/AGENTS.md`)
3. **Score** each item; produce category subtotals + total.
4. **Prioritized remediation**: every item missing → one remediation line, ordered by point-value (highest first).

## Output

```markdown
# Repo Golden-Path Score — {owner/repo}

**Total**: {N}/100 — {pass | needs-improvement | excellent}

| Category | Score | Notes |
|----------|-------|-------|
| Ownership + review | X/20 | ... |
| Branch protection | X/15 | ... |
| ... | ... | ... |

## Top remediation priorities

1. ...
2. ...
3. ...
```

Lands at `vault/research/github/YYYY-MM-DD-golden-path-{repo-slug}.md`.

## Composes with

- `gh api` for live inspection.
- `ghas-config-reviewer` — overlapping coverage; this is the broader scorecard.
- `dependabot-config-helper` — input to the Dependabot section.

## Acceptance test (for step 20 done-criteria)

Produce one scorecard for a hypothetical repo. Confirm all 8 categories scored, total computed, top remediation priorities listed in point-value order.
