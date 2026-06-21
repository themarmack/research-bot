---
name: monthly-regulator-watch
description: Monthly scheduled agent. Aggregates the past 30 days from US (and optionally EU/UK) financial regulators — OCC, FRB, FDIC, FFIEC, SEC, FINRA, CFPB, NYDFS, FCA, ECB — for guidance, comment periods, and enforcement actions touching software risk, AI/ML, third-party risk, or cyber. Runs on the 1st of each month. Output at vault/digests/monthly/YYYY-MM-DD-monthly-regulator-watch.md. Different from weekly-intelligence-digest: deeper regulator-only scope, with explicit comment-period tracking and enforcement-action analysis.
---

# monthly-regulator-watch

The companion monthly scheduled agent on the regulatory side. Where the monthly-copilot-changelog answers "what did vendors change?", this answers "what did regulators say?" Critical for tracking the forthcoming OCC + FRB + FDIC genAI RFI surfaced in [[2026-06-20-occ-frb-fdic-ai-posture-mid-2026]].

## Agent config (consumed by `scheduled-agent-runner`)

```yaml
agent_name: monthly-regulator-watch
cadence: monthly
schedule_hint: "1st of month, 08:00 local"
source_filter:
  topic_tags: [regulator, ai-governance, compliance-framework]
  min_tier: 1
  source_ids:
    - federalreserve-press
    - occ-news-releases     # currently verified: false; this skill will surface that and prompt to fix
    - ffiec-press
  max_items_per_source: 25
verify_loadbearing: true    # interpretive claims about what guidance means get the 3-vote treatment
curate_findings: true
digest_template_overrides:
  template: monthly-regulator-watch
  why_you_care_extra: |
    For each item, categorize:
    - Guidance — proposed or finalized. Comment period open? When does it close?
    - Enforcement action — what's the underlying conduct + which control failed?
    - RFI / discussion paper — what response does the org need to organize?
    Track open comment periods explicitly in the "Open Loops" section.
```

## Output document structure

```markdown
# Monthly Regulator Watch — {month}

## At a glance
{N items total; M new guidance; K enforcement; J RFIs / open comment periods}

## New guidance

### {guidance title} — {regulator}
**Status**: proposed | finalized | guidance-as-published
**Comment period**: {date range, if applicable}
**What it says**: {1-2 sentences}
**Compliance-relevant implication**: {control / policy connection}
**Source**: {tier 1 URL}

## Enforcement actions

### {action title} — {regulator}
**Subject**: {institution + amount + conduct}
**Underlying control failure**: {what control should have prevented this}
**Compliance-relevant lesson**: {what to check internally}
**Source**: {tier 1 URL}

## Open comment periods / RFIs

| Topic | Regulator | Opens | Closes | Internal lead |
|-------|-----------|-------|--------|---------------|

## Items for awareness (no action)
- {one-liners}

## Cross-references to vault
- [[2026-06-20-occ-frb-fdic-ai-posture-mid-2026]] updates
- Facts staged for memory-curator
- Stakeholder update items queued
```

## Composes with

Same Phase-1 foundation. Cross-feeds `financial-regulator-watch` (the on-demand researcher) — when a monthly entry needs deeper coverage, that's the skill to invoke.

## Acceptance test (for step 21 done-criteria)

One monthly digest exercised against a 30-day window. Confirm: items categorized by type (guidance / enforcement / RFI); open comment periods tracked in a dedicated section; compliance-relevant implications per item.
