---
name: codeql-onboarding-helper
description: Given a target repo's stack + risk profile, decide default vs advanced CodeQL setup, recommend a query suite (code-scanning / security-extended / security-and-quality), select custom packs (community + org's internal), document the alert triage workflow, and define the exception process. Produces an onboarding plan ready to hand to the repo owner. Use during repo GHAS onboarding or when refactoring a repo's existing CodeQL setup that's drowning in low-signal alerts or missing real ones.
---

# codeql-onboarding-helper

A Category 3 ops tool. CodeQL setup has more decision points than people realize: setup type, query suite, custom packs, triage routing, exception process. Getting them wrong on a regulated-data repo means false negatives (real findings missed) or false-positive saturation (real findings buried). This skill makes the decision tree explicit.

## When to use

- Onboarding a new repo to GHAS code scanning.
- Refactoring an existing CodeQL setup that's been ignored or under-tuned.
- Org-wide consistency audit: are repos using the right query suite for their language + risk?
- Planning a custom pack rollout (org-specific patterns).

## When NOT to use

- Specific alert triage / dismissal → out of scope.
- Building a custom CodeQL query → `codeql-pattern-finder`.
- Workflow-level Actions security → `actions-workflow-hardener`.
- Org-wide GHAS posture → `ghas-config-reviewer`.

## Decision matrix

### Default setup vs advanced setup

| Use default setup if | Use advanced setup if |
|----------------------|----------------------|
| Standard build (no custom JDK pin, no proprietary build system) | Custom build command, monorepo with non-standard layout |
| GitHub-hosted runners are acceptable | Build requires private-network access (internal Maven, internal pip) |
| No custom packs needed | Custom CodeQL packs (community or org-internal) needed |
| Standard query suite is sufficient | Need to combine multiple suites or modify per-language |
| Repo's languages are all CodeQL-default-supported | Build matrix is complex |

For a regulated organization, **advanced setup** is the more common right answer because of internal-Maven/npm registry access requirements for the build step.

### Query suite selection

| Suite | When to use | Trade-off |
|-------|-------------|-----------|
| `code-scanning` (default) | Low-stakes repos, exploratory phases | Misses some real findings |
| `security-extended` | **Default for regulated-data repos** | More findings, higher false-positive rate; requires triage discipline |
| `security-and-quality` | Repos where code quality alerts are wanted alongside security | Largest alert volume; reserve for repos with dedicated review capacity |

### Custom pack recommendation

- **Community packs**: `github/codeql` contains the standard packs; per-language community packs at `codeql-packs/*` cover ecosystem-specific patterns (e.g. spring/log4j hardening).
- **Bank-internal packs** (TBD; not built yet): cover org-specific patterns — internal data-access wrappers, deprecated crypto APIs, internal auth token misuse. Worth building once the SDLC modernization program has a critical mass of repeated patterns to encode.

### Alert triage workflow

For each repo:
- **Severity routing**: critical/high → CODEOWNERS-assigned reviewer within 7 days; medium → 30 days; low → 90 days or auto-dismiss per [[2026-06-20-dependabot-best-practices-regulated-org]] auto-triage pattern.
- **Dismissal rules**: dismissals require a comment with category (false-positive | won't-fix | mitigated | duplicate). The comment becomes audit evidence.
- **Exception process**: a finding dismissed as `won't-fix` requires a `decisions/` note via [`copilot-exception-handler`](../copilot-exception-handler/SKILL.md)-equivalent pattern (a future `ghas-exception-handler` would generalize this).

## Output

An onboarding plan note at `vault/research/github/YYYY-MM-DD-codeql-onboarding-{repo-slug}.md`. Structure:

1. **Repo context** — language(s), stack, risk profile, current state.
2. **Setup-type decision** — default vs advanced, with rationale.
3. **Query suite recommendation** — which suite + why.
4. **Custom packs** — list + rationale.
5. **Sample workflow** (if advanced setup) — ready-to-commit `.github/workflows/codeql.yml`.
6. **Triage workflow** — concrete rules for this repo.
7. **Exception process** — how this repo's team handles `won't-fix` findings.
8. **Acceptance checklist** — what "onboarded" means for this repo.

## Composes with

- [`ghas-config-reviewer`](../ghas-config-reviewer/SKILL.md) — code-scanning baseline check item.
- [`actions-workflow-hardener`](../actions-workflow-hardener/SKILL.md) — when the CodeQL workflow itself needs review.
- [`codeql-pattern-finder`](../codeql-pattern-finder/SKILL.md) — for custom-pack rollout.

## Acceptance test (for step 19 done-criteria)

Produce one onboarding plan for a hypothetical target (e.g., Payments primary service repo). Confirm all 8 sections present, setup-type decision justified, and at minimum one compliance-relevant custom pack recommendation.
