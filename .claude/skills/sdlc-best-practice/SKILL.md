---
name: sdlc-best-practice
description: On-demand Category 1 researcher for narrow SDLC concerns — trunk-based development, ephemeral environments, IaC promotion patterns, secrets-handling lifecycle, golden paths / platform engineering, branch strategies, change-freeze patterns, feature-flag governance, blue-green vs canary. For a focused question, produces a research note with current-state-of-practice + regulated-org constraints + recommended approach. Output at vault/research/sdlc-best-practice/YYYY-MM-DD-{slug}.md. Use when the user asks to research a general SDLC practice or pattern that no topic-specific researcher covers — producing a fresh, cited research note — as opposed to Copilot (copilot-deep-dive), GitHub platform (github-platform-watch), regulator (financial-regulator-watch), or supply-chain (supply-chain-security-watch) questions.
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
- AppSec specific → the AppSec review skills (`threat-model-helper`, `secure-design-reviewer`, `secure-coding-standard-checker`, `iac-security-reviewer`, `secrets-hygiene-reviewer`, `sbom-reviewer`)

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the question's key terms across `vault/research/sdlc-best-practice/**`, `vault/insights/**` (conference-talk and learning notes often cover SDLC practices), relevant `vault/facts/**` entities for the practice in question, and recent `vault/digests/**` (last 90 days).
   - Backlink check on the practice's entities (e.g. `[[trunk-based-development]]`, `[[feature-flags]]`).
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: DORA / Accelerate research, Google SRE / engineering practice docs, ThoughtWorks Technology Radar, vendor engineering blogs from named practitioners, NIST 800-218 SSDF where the practice touches secure development.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - SDLC best practice is opinion-dense; any "state of practice" claim from a secondary source gets the full 3-vote treatment before it backs a policy recommendation.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/sdlc-best-practice/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic: sdlc-best-practice`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/sdlc-best-practice/`:
   - Any verified fact-typed claim → `_inbox/sdlc-best-practice/{timestamp}-{slug}.md` with `suggested_surface: facts` and a `suggested_path` under the matching `facts/` entity.
   - `memory-curator` decides on its next sweep.

## Compliance-relevant framing per finding

For each finding answer:
1. What does best-practice look like outside the org?
2. What regulated-environment constraint changes the picture (SOX evidence, change-management, RTO/RPO requirements)?
3. What's the org's current posture (per vault facts + the user's knowledge)?
4. Recommended approach considering the constraints.

## Composes with

Standard Phase-1 foundation. Naturally pairs with `incident-postmortem-research` (when the question is incident-triggered).

- [`executive-summary-writer`](../executive-summary-writer/SKILL.md) — **only when the user explicitly asks for an exec summary** (never auto-invoked after vault write). Takes the just-written research note's path and produces a 1-page summary tuned to a named audience (CISO, VP Eng, etc.).
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 31 done-criteria)

The Payments KB review trilogy + 11 prior research notes serve as exemplars of what this skill produces. Live exercise deferred to the next on-demand SDLC question.
