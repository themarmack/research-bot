---
name: github-platform-watch
description: On-demand Category 1 researcher focused on the GitHub platform (NOT Copilot — that's copilot-deep-dive). Covers Actions, Advanced Security (CodeQL, Dependabot, secret scanning, push protection, security campaigns), Audit Log, Billing, Packages, Issues / Projects, Enterprise EMU/SAML, repository governance. Enforces the Obsidian-first contract: vault-querier first against vault/facts/github/ and vault/research/github/, then web research only for confirmed gaps. Findings land at vault/research/github/YYYY-MM-DD-{slug}.md; verified facts get staged to _inbox/ for memory-curator promotion. Use when the user asks to research a GitHub platform (non-Copilot) topic in depth — Actions, GHAS posture, audit log, billing, EMU/SAML, repo governance — producing a fresh, cited research note — as opposed to Copilot questions (copilot-deep-dive), a single GHAS feature deep-dive (ghas-feature-research), or auditing a live repo/org configuration (ghas-config-reviewer, github-org-audit-runner).
---

# github-platform-watch

On-demand deep research on the GitHub platform — Actions, GHAS, Audit Log, Billing, Issues, Enterprise EMU/SAML, repository governance. Same workflow as [`copilot-deep-dive`](../copilot-deep-dive/SKILL.md) but a different topic surface. Most "what's the current state of <GitHub platform feature> for an enterprise / regulated org?" questions land here.

## When to use

- A GitHub platform question that's not Copilot-specific (Copilot questions → `copilot-deep-dive`).
- Comparing a feature's current state to the org's existing posture (e.g., "should we move from CodeQL default setup to advanced setup?").
- A net-new question that should become durable knowledge in `vault/facts/github/`.

## When NOT to use

- Copilot questions → `copilot-deep-dive`.
- Specific repo audits → [`repo-golden-path-scorer`](../repo-golden-path-scorer/SKILL.md).
- Workflow hardening for a specific YAML file → [`actions-workflow-hardener`](../actions-workflow-hardener/SKILL.md).

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the question's key terms across `vault/facts/github/**`, `vault/research/github/**`, `vault/insights/**`, and recent `vault/digests/**` for GitHub-tagged items (last 90 days).
   - Backlink check on `[[github]]` and the question's entities (e.g. `[[github-actions]]`, `[[emu]]`).
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs from the fact's frontmatter). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: GitHub Docs, the GitHub blog changelog, GitHub's public roadmap, official GitHub security advisories.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - Any claim destined for `vault/facts/github/` must pass verification.
   - Claims from GitHub's own docs/changelog are exempt (the vendor IS the authority).
   - Claims from secondary sources (analyst blogs, practitioner posts) get the full 3-vote treatment.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/github/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic` from the taxonomy below, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/github-platform-watch/`:
   - Any verified fact-typed claim → `_inbox/github-platform-watch/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/github/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

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
