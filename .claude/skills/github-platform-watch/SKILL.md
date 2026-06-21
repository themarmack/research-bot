---
name: github-platform-watch
description: On-demand Category 1 researcher focused on the GitHub platform (NOT Copilot — that's copilot-deep-dive). Covers Actions, Advanced Security (CodeQL, Dependabot, secret scanning, push protection, security campaigns), Audit Log, Billing, Packages, Issues / Projects, Enterprise EMU/SAML, repository governance. Enforces the Obsidian-first contract: vault-querier first against vault/facts/github/ and vault/research/github/, then web research only for confirmed gaps. Findings land at vault/research/github/YYYY-MM-DD-{slug}.md; verified facts get staged to _inbox/ for memory-curator promotion.
---

# github-platform-watch

On-demand deep research on the GitHub platform — Actions, GHAS, Audit Log, Billing, Issues, Enterprise EMU/SAML, repository governance. Same workflow as [`copilot-deep-dive`](../copilot-deep-dive/SKILL.md) but a different topic surface. Most "what's the current state of <GitHub platform feature> for an enterprise / regulated org?" questions land here.

## When to use

- A GitHub platform question that's not Copilot-specific (Copilot questions → `copilot-deep-dive`).
- Comparing a feature's current state to the org's existing posture (e.g., "should we move from CodeQL default setup to advanced setup?").
- A net-new question that should become durable knowledge in `vault/facts/github/`.

## When NOT to use

- Copilot questions → `copilot-deep-dive`.
- Specific repo audits → `repo-golden-path-scorer` (planned).
- Workflow hardening for a specific YAML file → `actions-workflow-hardener` (planned).

## Obsidian-first workflow

Identical to `copilot-deep-dive` but with a different scope. See that skill for the full mandatory steps.

Key difference: the **vault subfolder is `github/`**, not `copilot/`. The query first targets `vault/facts/github/**`, `vault/research/github/**`, and recent `vault/digests/**` for GitHub-tagged items.

## Topic taxonomy

When writing research notes, use the `topic` frontmatter field consistently. For this skill, valid topics include:

- `github-actions` — Actions runners, workflows, marketplace, OIDC, hardening.
- `ghas-codeql` — CodeQL specifically.
- `ghas-dependabot` — Dependabot config, alerts, security updates.
- `ghas-secret-scanning` — push protection, partner patterns, custom patterns.
- `github-audit-log` — admin audit, security log, IP allow list, etc.
- `github-billing` — usage metrics, license assignment, cost.
- `github-enterprise` — EMU, SAML, SCIM, runner groups, policies.
- `github-repo-governance` — branch protection, CODEOWNERS, rulesets, allowed actions.

The research note's path will be `vault/research/github/YYYY-MM-DD-{slug}.md` regardless of topic — the topic frontmatter field is what `vault-querier` filters on later.

## Compliance-relevant framing

Same as `copilot-deep-dive`. Every finding ties to SR 11-7 / FFIEC / OCC / SOX ITGC / NYDFS 500 / data residency where applicable; `#general` tag otherwise.

## Composes with

Same as `copilot-deep-dive`. The two skills share the on-demand research pattern; only the topic scope differs.

## Acceptance test (for step 11 done-criteria)

One live end-to-end research run produces a research note at `vault/research/github/YYYY-MM-DD-{slug}.md` with the same structure as `copilot-deep-dive`'s acceptance.
