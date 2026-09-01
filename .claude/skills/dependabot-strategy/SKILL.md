---
name: dependabot-strategy
description: On-demand Category 1 researcher focused on Dependabot best practices for a regulated organization — triage workflows, grouped-update strategies, auto-merge gates, ecosystem coverage, private-registry integration, cooldown periods for zero-day waiting, and the auto-triage rules that turn alert volume into actionable signal. Enforces Obsidian-first contract. Findings land at vault/research/dependabot/YYYY-MM-DD-{slug}.md; verified facts get staged for memory-curator promotion to vault/facts/ghas-dependabot/. Used by dependabot-config-helper as the source of defaults. Use when the user asks a strategic, policy, triage, or tooling question about Dependabot that needs a research-grade answer with citations — not when generating or reviewing a concrete dependabot.yml (dependabot-config-helper) or researching a non-Dependabot GHAS feature (ghas-feature-research).
---

# dependabot-strategy

The research side of the Dependabot pair. Produces the policy / strategy / triage research notes that the `dependabot-config-helper` skill consumes when generating actual `dependabot.yml` files. Treats Dependabot as a control surface, not just a config file — the *why* drives the *what*.

## When to use

- Strategic question: "Should we adopt grouped updates? What's the cost?"
- Policy question: "What's the right schedule cadence for ecosystem X in a SOX-regulated environment?"
- Triage question: "We have 12,000 open Dependabot alerts — how do other regulated orgs handle this?"
- Tooling question: "What auto-triage / auto-merge gates are people running in 2026?"

## When NOT to use

- Specific `dependabot.yml` generation — that's `dependabot-config-helper`.
- Individual alert triage — out of this skill's scope (and no skill in the catalog covers it).
- GHAS-wide strategy beyond Dependabot — broader question, [`ghas-feature-research`](../ghas-feature-research/SKILL.md).

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the question's key terms across `vault/facts/ghas-dependabot/**`, `vault/research/dependabot/**`, `vault/research/github/**` (older Dependabot notes live there), and recent `vault/digests/**` (last 90 days — `daily-cve-digest` output often carries Dependabot-coverage observations).
   - Backlink check on `[[dependabot]]` and the question's entities (ecosystems, registries).
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs from the fact's frontmatter). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: GitHub Docs (Dependabot reference), the GitHub blog changelog, GitHub's public roadmap.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - GitHub's own docs are tier-1 (no verification); practitioner write-ups on triage workflows and auto-merge gating get the full 3-vote treatment before informing a policy default.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/dependabot/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic: ghas-dependabot`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/dependabot-strategy/`:
   - Any verified fact-typed claim → `_inbox/dependabot-strategy/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/ghas-dependabot/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

## Topic taxonomy

For the research note's `topic` field, use `ghas-dependabot` (matching the source-registry tag).

## Compliance-relevant framing

Every finding ties Dependabot's behavior to:
- SOX ITGC (change-management evidence for production dependencies)
- FFIEC IT Handbook (vendor / third-party risk)
- Internal SLA for security-update patching (typically 7/30/90 days by severity)
- Specific ecosystems the org's stack uses (Java/Maven, Node/npm, Python/pip, Go, Docker)

## Composes with

The Phase-1 foundation named in the workflow above (`vault-querier`, `source-fetcher` + `prompt-injection-guard`, `claim-extractor` + `verify-claim`, `digest-writer` → `vault-writer`, `_inbox/` + `memory-curator`). Output feeds `dependabot-config-helper`.

## Acceptance test (for step 18 done-criteria)

One live research note covering at minimum: grouped-update best practices, schedule cadence guidance per ecosystem, auto-merge gating policy, private-registry integration, and at least one compliance-relevant compliance angle.
