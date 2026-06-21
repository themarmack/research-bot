---
name: copilot-metrics-analyzer
description: Take raw Copilot Usage Metrics API output (per-user, daily granularity, including the new `ai_credits_used` field) and produce structured findings — top cost/usage anomalies, per-dev chargeback math with the 10% data-residency surcharge applied, and actionable recommendations. Uses facts from `vault/facts/copilot/` (usage-metrics-ai-credits-per-user, data-residency-surcharge) so cost math reflects the org's actual configuration, not generic per-seat assumptions. Use weekly for monitoring or ad-hoc for cost-attribution conversations with finance.
---

# copilot-metrics-analyzer

A Category 3 ops tool. The org's Copilot Enterprise tenant produces usage metrics; this skill translates raw API output into the answers finance / ops / managers actually ask: "who's expensive, who's idle, are we within budget, what's the chargeback per BU?"

## When to use

- Weekly cost monitoring during a rollout (Phase 3 / Phase 5 of [`copilot-rollout-playbook`](../copilot-rollout-playbook/SKILL.md)).
- Cost-attribution conversation with finance — "show me the per-LOB Copilot spend with the org's actual surcharge applied."
- Identifying dormant licenses for cost recovery.
- Outlier detection — anomalously high acceptance rate or AI-credits consumption that warrants 1:1 conversation.

## When NOT to use

- Strategic Copilot adoption decisions — those are research, not metrics.
- Performance / latency monitoring — that's a different signal entirely.
- Individual developer evaluation — these metrics are aggregate, not per-developer-quality.

## Input

The Copilot Usage Metrics API JSON, per-user daily granularity. Required fields (per [[usage-metrics-ai-credits-per-user]]):

```json
[
  {
    "user": "dev1@example.com",
    "date": "2026-06-19",
    "active": true,
    "suggestions_shown": 142,
    "suggestions_accepted": 38,
    "chat_turns": 12,
    "ai_credits_used": 18.4
  }
]
```

Plus optional context the user provides:
- `period_start` / `period_end` — analysis window
- `business_units` — mapping of user → BU for chargeback
- `cost_per_credit` — the org's actual contracted rate
- `data_residency_active` — true/false (affects surcharge math)

## Bank-specific constants

Loaded from `vault/facts/copilot/`:

- **[[data-residency-surcharge]]** — 10% multiplier when data residency is active
- **[[usage-metrics-ai-credits-per-user]]** — API field structure

## Findings the analyzer produces

### Top-3 cost/usage findings

A structured list of the 3 most action-worthy patterns in the data. Default checks:

1. **High-credit outliers** — users in the top 5% of `ai_credits_used` for the period. Surface their consumption + acceptance rate; flag if acceptance rate is low (high credits + low acceptance suggests over-reliance / misuse).
2. **Dormant licenses** — users with active license assignment but `active: false` for ≥7 consecutive days. Each dormant license is recoverable cost.
3. **Acceptance-rate anomalies** — users with acceptance rate >2σ from the team mean (high OR low). High = potential blind-acceptance; low = workflow mismatch or training gap.

### Per-dev chargeback math

For each business unit:

```
unit_credits = sum(ai_credits_used) over users in unit
unit_credits_with_surcharge = unit_credits * (1.10 if data_residency_active else 1.00)
unit_cost = unit_credits_with_surcharge * cost_per_credit
```

Output a per-BU table sortable by credits / cost / users / avg-credits-per-user.

### Recommendations

Concrete action items:
- Specific dormant users to reclaim seats from (with date range of dormancy).
- Specific high-credit outliers to follow up with (link to user, recent activity summary).
- Team-level patterns worth surfacing in the next [`stakeholder-update-writer`](../stakeholder-update-writer/SKILL.md) update.

## Output structure

```markdown
# Copilot Metrics Analysis — {period}

## TL;DR
- {bullet 1}
- {bullet 2}
- {bullet 3}

## Top-3 findings
1. ...
2. ...
3. ...

## Chargeback math (by BU)
| BU | Active users | Credits used | Surcharge (10%) | Total cost |
|----|--------------|--------------|-----------------|------------|

## Recommendations
- ...

## Methodology
- Surcharge applied: 10% (data residency active per [[data-residency-surcharge]])
- Source fact: [[usage-metrics-ai-credits-per-user]]
- Cost per credit: ${cost_per_credit}
- Period: {start} → {end}
- Users analyzed: N
```

Output lands at `vault/research/copilot/YYYY-MM-DD-metrics-{period-slug}.md`.

## Composes with

- `vault-querier` — load facts (data-residency-surcharge, usage-metrics structure).
- `copilot-rollout-playbook` — Phase 3 / Phase 5 cycles invoke this.
- `stakeholder-update-writer` — input to exec-tier cost summaries.

## Acceptance test (for step 16 done-criteria)

Take a sample `ai_credits_used` JSON (8-12 users across 2 BUs, 7-day window). Produce:
- Top-3 findings with at least one of each type (high-credit / dormant / acceptance-anomaly) if the sample contains them.
- Per-BU chargeback table with the 10% surcharge correctly applied (i.e., the math math).
- 3-5 concrete recommendations.
- Methodology block citing the facts used.
