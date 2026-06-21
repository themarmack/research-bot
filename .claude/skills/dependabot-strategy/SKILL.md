---
name: dependabot-strategy
description: On-demand Category 1 researcher focused on Dependabot best practices for a regulated organization — triage workflows, grouped-update strategies, auto-merge gates, ecosystem coverage, private-registry integration, cooldown periods for zero-day waiting, and the auto-triage rules that turn alert volume into actionable signal. Enforces Obsidian-first contract. Findings land at vault/research/github/YYYY-MM-DD-dependabot-{slug}.md; verified facts get staged for memory-curator promotion to vault/facts/ghas-dependabot/. Used by dependabot-config-helper as the source of defaults.
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
- Individual alert triage — that's not this skill's scope; nor any other yet planned.
- GHAS-wide strategy beyond Dependabot — broader question, `ghas-feature-research` (planned).

## Obsidian-first workflow

Same as other Category 1 researchers (see [`copilot-deep-dive`](../copilot-deep-dive/SKILL.md)). Query `vault/facts/ghas-dependabot/`, `vault/research/github/` first. Web research only on gaps.

## Topic taxonomy

For the research note's `topic` field, use `ghas-dependabot` (matching the source-registry tag).

## Compliance-relevant framing

Every finding ties Dependabot's behavior to:
- SOX ITGC (change-management evidence for production dependencies)
- FFIEC IT Handbook (vendor / third-party risk)
- Internal SLA for security-update patching (typically 7/30/90 days by severity)
- Specific ecosystems the org's stack uses (Java/Maven, Node/npm, Python/pip, Go, Docker)

## Composes with

Same Phase-1 foundation as other Category 1 researchers. Output feeds `dependabot-config-helper`.

## Acceptance test (for step 18 done-criteria)

One live research note covering at minimum: grouped-update best practices, schedule cadence guidance per ecosystem, auto-merge gating policy, private-registry integration, and at least one compliance-relevant compliance angle.
