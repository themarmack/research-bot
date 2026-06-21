---
name: sdlc-best-practice
description: On-demand Category 1 researcher for narrow SDLC concerns — trunk-based development, ephemeral environments, IaC promotion patterns, secrets-handling lifecycle, golden paths / platform engineering, branch strategies, change-freeze patterns, feature-flag governance, blue-green vs canary. For a focused question, produces a research note with current-state-of-practice + regulated-org constraints + recommended approach. Output at vault/research/sdlc-best-practice/YYYY-MM-DD-{slug}.md.
---

# sdlc-best-practice

The generalist SDLC research skill. For any narrow SDLC question that doesn't fit a more specific topic (Copilot → `copilot-deep-dive`, GitHub platform → `github-platform-watch`, regulator → `financial-regulator-watch`), this is the on-demand researcher.

## When to use

- Specific SDLC practice question: "what's current state of feature-flag governance for regulated apps?"
- Architecture-review prep: a pattern is proposed; research current state-of-practice.
- Internal-policy drafting: backing a new SDLC policy with current best-practice references.
- After an incident: was the org's posture aligned with current practice or behind?

## When NOT to use

- Copilot-specific → `copilot-deep-dive`
- GitHub platform → `github-platform-watch`
- Regulator → `financial-regulator-watch` / `ai-governance-research`
- Supply-chain → `supply-chain-security-watch`
- AppSec specific → step-24-27 skills

## Obsidian-first workflow

Same Phase-1 pattern. Topic: `sdlc-best-practice`.

## Compliance-relevant framing per finding

For each finding answer:
1. What does best-practice look like outside the org?
2. What regulated-environment constraint changes the picture (SOX evidence, change-management, RTO/RPO requirements)?
3. What's the org's current posture (per vault facts + the user's knowledge)?
4. Recommended approach considering the constraints.

## Composes with

Standard Phase-1 foundation. Naturally pairs with `incident-postmortem-research` (when the question is incident-triggered).

- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 31 done-criteria)

The Payments KB review trilogy + 11 prior research notes serve as exemplars of what this skill produces. Live exercise deferred to the next on-demand SDLC question.
