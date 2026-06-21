---
name: ghas-feature-research
description: On-demand Category 1 researcher for a specific GitHub Advanced Security feature — secret scanning push protection, code scanning autofix, security campaigns, dependency review action, security advisories database, custom auto-triage rules. For a chosen feature, produces a research note with current state, rollout caveats, regulated-org applicability, and recommendations. Output at vault/research/ghas/YYYY-MM-DD-{feature-slug}.md. Composes with ghas-config-reviewer (baseline-checking side) and the various GHAS-touching ops skills.
---

# ghas-feature-research

A focused-on-one-feature research skill. Where `ghas-config-reviewer` checks baseline posture and `github-platform-watch` covers the whole platform, this skill goes deep on a specific GHAS feature when adoption / rollout / tuning needs a research-grade answer.

## When to use

- New GHAS feature announced (e.g., code-scanning autofix in 2025; security campaigns in 2026).
- Rollout planning for an existing-but-underused GHAS feature.
- Deciding default vs advanced for a specific GHAS component on a target repo set.
- Pre-procurement / TPRM review when a GHAS feature is a contract dimension.

## Topic taxonomy

- `secret-scanning` — push protection, partner patterns, custom patterns
- `code-scanning` — default-setup, advanced-setup, autofix
- `dependency-review` — PR-time dep review, configuration
- `security-campaigns` — newer aggregated-finding workflow
- `dependabot` — already covered in detail by `dependabot-strategy`; route there
- `auto-triage-rules` — alert-volume management

## Obsidian-first workflow

Same Phase-1 pattern.

## Compliance-relevant framing per finding

For each finding:
1. Does adopting this change `ghas-config-reviewer`'s baseline?
2. Does it affect `repo-golden-path-scorer`'s rubric weights?
3. Does it affect SOX evidence flow?
4. Does it require user-facing comms?

## Composes with

- `ghas-config-reviewer` — baseline owner.
- `codeql-onboarding-helper` — for code-scanning features.
- `dependabot-strategy` — for Dependabot-adjacent features.
- `github-platform-watch` — for broader platform context.

## Acceptance test (for step 29 done-criteria)

SKILL.md describes the per-feature research workflow + topic taxonomy. Live exercise deferred to first specific feature-research invocation.
