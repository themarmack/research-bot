---
name: ghas-feature-research
description: On-demand Category 1 researcher for a specific GitHub Advanced Security feature — secret scanning push protection, code scanning autofix, security campaigns, dependency review action, security advisories database, custom auto-triage rules. For a chosen feature, produces a research note with current state, rollout caveats, regulated-org applicability, and recommendations. Output at vault/research/ghas/YYYY-MM-DD-{feature-slug}.md. Composes with ghas-config-reviewer (baseline-checking side) and the various GHAS-touching ops skills. Use when the user asks to research a single GHAS feature in depth — adoption, rollout, tuning, regulated-org caveats — producing a fresh, cited research note; not for checking a repo or org config against the baseline (ghas-config-reviewer), Dependabot strategy questions (dependabot-strategy), or platform-wide GitHub questions (github-platform-watch).
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

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the feature's key terms across `vault/research/ghas/**`, `vault/research/github/**`, `vault/facts/github/**`, `vault/facts/ghas-dependabot/**`, and recent `vault/digests/**` (last 90 days — `biweekly-codeql-community-pulse` and `weekly-intelligence-digest` often carry GHAS feature news).
   - Backlink check on the feature's entity (e.g. `[[secret-scanning]]`, `[[code-scanning]]`).
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs from the fact's frontmatter). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: GitHub Docs (GHAS reference), the GitHub blog changelog, GitHub's public roadmap.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - GitHub's own docs and changelog are tier-1 (no verification); rollout-experience posts and analyst takes on feature maturity get the full 3-vote treatment.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/ghas/YYYY-MM-DD-{feature-slug}.md`
   - Frontmatter per `research.yml` schema: `topic` from the taxonomy above, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/ghas-feature-research/`:
   - Any verified fact-typed claim → `_inbox/ghas-feature-research/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/github/{predicate}.md` (or `facts/ghas-dependabot/` for Dependabot-adjacent facts).
   - `memory-curator` decides on its next sweep.

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
