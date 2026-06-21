---
name: quarterly-ai-coding-landscape
description: Quarterly scheduled agent that produces a long-form (~2000-3500 word) landscape report on AI coding tools (Copilot + Cursor + Windsurf + Cody + JetBrains AI + Amazon Q Developer + emerging), suitable for forwarding to leadership (CIO / CTO / eng VP). Synthesizes the quarter's vault accumulation: weekly intelligence digests, voices intelligence, frontier-model research, regulator posture, and the org's own rollout state. Runs at the start of each quarter; lands at vault/digests/quarterly/YYYY-MM-DD-ai-coding-landscape-Q{N}-{YYYY}.md.
---

# quarterly-ai-coding-landscape

The leadership-facing artifact. Most stakeholders don't read weekly digests — they want a quarterly synthesis with explicit takeaways and forward-looking direction. This skill produces that, drawing on the quarter's vault accumulation rather than re-doing the research.

## Agent config (consumed by `scheduled-agent-runner`)

```yaml
agent_name: quarterly-ai-coding-landscape
cadence: quarterly
schedule_hint: "first business day of quarter, 09:00 local"
source_filter:
  custom: vault                        # this skill's source IS the vault
  surfaces: [digests, research, facts, decisions, insights]
  window_days: 92                      # full quarter
verify_loadbearing: false              # synthesis, not new facts
curate_findings: false                 # output is a synthesis, not new facts to promote
digest_template_overrides:
  template: leadership-landscape
  why_you_care_extra: |
    Target audience: CIO / CTO / eng VP. Voice: declarative, dense, executive-tier.
    Structure: TL;DR at top, sections explicitly forward-looking ("what to expect Q+1").
    NO vendor marketing language. Every claim sourced.
```

## Document structure

```markdown
# AI Coding Landscape — Q{N} {YYYY}

**Period**: {start} → {end}
**Audience**: leadership; safe to forward.

## TL;DR (≤200 words)
The 3-5 sentences a CIO needs to walk into a board conversation prepared.

## State of the AI coding tools market

Vendor section — current state of:
- GitHub Copilot (the org's primary)
- Cursor / Windsurf / Cody / JetBrains AI / Amazon Q (the alternatives and what they're winning on)
- Frontier model context (which models route where)

## What changed this quarter

Cross-vault synthesis. Per topic:
- Specific changes citing vault facts/research/digests
- Bank-impact assessment

## Regulatory environment

Per `financial-regulator-watch` + `ai-governance-research` quarterly accumulation:
- What's locked in (MRM revisions, residency posture, sector-specific guidance)
- What's pending (RFI signals, comment periods)

## Org's own position

The internal state — Copilot rollout progress (per `copilot-metrics-analyzer` quarterly summary), exception backlog, GHAS posture (per `repo-golden-path-scorer` portfolio summary), incidents (from `events/`).

## What to expect Q+1

Forward-looking projections grounded in this quarter's findings:
- Model deprecations / new model rollouts
- Regulator activity expected (RFIs publishing, comment windows opening)
- The org's own roadmap milestones

## Strategic recommendations (2-4)

Each recommendation: the decision, the rationale, the risk of inaction.

## Sources

All vault notes cited inline via [[wikilinks]], no separate URL bibliography (sources live in the linked notes' frontmatter).
```

## Composes with

Reads from the vault — does NOT do new fetches. The quarter's accumulated weekly-intelligence-digests, voices-watcher digests, weekly-reviews, and on-demand research notes are the source material.

Output feeds:
- `stakeholder-update-writer` — exec tier quarterly cycle
- `decision-memo-writer` (planned) — strategic recommendations sometimes need supporting decision memos

## Acceptance test (for step 23 done-criteria)

One quarterly landscape report exercised against the toolkit's bootstrap quarter (covers a sub-quarter window given the toolkit started 2026-06-20). Confirm structure, length (1500-3500 words), TL;DR present, 2-4 strategic recommendations, exclusively vault-sourced citations.
