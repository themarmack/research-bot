---
name: weekly-intelligence-digest
description: The flagship weekly scheduled agent. Polls high-signal sources across GitHub/Copilot/Anthropic/OpenAI/regulators/supply-chain, surfaces what changed in the past 7 days, and produces a single ranked markdown digest at vault/digests/weekly/YYYY-MM-DD-weekly-intelligence-digest.md framed with the regulated-org lens. Composes the full Phase-1 foundation via scheduled-agent-runner. Run weekly on Monday morning (or invoke ad-hoc).
---

# weekly-intelligence-digest

The flagship scheduled agent — the one the user explicitly asked for in the original ideation. Every Monday morning, it surfaces what changed in the past 7 days across the sources that matter for SDLC modernization at a regulated organization, framed in plain language with the compliance-relevant lens.

## Agent config (consumed by `scheduled-agent-runner`)

```yaml
agent_name: weekly-intelligence-digest
cadence: weekly
schedule_hint: "Monday 07:00 local"
source_filter:
  topic_tags:
    - github
    - copilot
    - ghas
    - frontier-model
    - ai-coding-tools
    - regulator
    - ai-governance
    - supply-chain
    - compliance-framework
  min_tier: 2          # tier 1 + tier 2 — skip unverified tier-3
  max_items_per_source: 5
verify_loadbearing: true       # Top-3 items get verify-claim (3-vote refute)
curate_findings: true          # Stage promotable claims to _inbox/ for memory-curator
digest_template_overrides:
  why_you_care_extra: |
    Frame every "Why You Care" line through the lens of: SDLC modernization for a
    large engineering organization, GitHub admin operations (Copilot/CodeQL/Dependabot/GHAS),
    or US financial regulation (SR 11-7 model risk, FFIEC, OCC, NYDFS 500, SOX ITGC).
    If a finding doesn't tie to one of these, drop it from the digest — it belongs in
    research/ or a different surface, not the weekly intelligence brief.
```

## Intent

A Monday-morning brief the user reads in 5 minutes:
1. **What changed** last week that they need to know about — Copilot release, Anthropic model launch, FFIEC guidance, OpenSSF advisory affecting the org's stack.
2. **Why they care** — the compliance-relevant implication, not the marketing copy.
3. **Sources** with credibility tier badges so claims are auditable months later.

This is the canonical example of [Use Case 1 — Scheduled weekly research](../../skills-plan.md#use-cases).

## TL;DR ranking rules

Pick the top 3 items for the TL;DR by signal:
1. **Regulator action** that mandates or strongly suggests a control change.
2. **Vendor product change** that changes the answer to a Copilot-FAQ-style question the user fields regularly (data handling, audit log, content exclusion, IP indemnity).
3. **Frontier-model release** with implications for which models Copilot/Cursor/etc. will route to.
4. **Supply-chain incident or advisory** affecting the org's declared tech stack.

If fewer than 3 high-signal items, leave TL;DR with fewer bullets — don't pad with filler.

## "Why You Care" examples

Good (concrete, compliance-relevant):

> **Copilot Enterprise audit log S3 export** — Regulated buyers can now ingest into SIEM via direct S3 + KMS, replacing scheduled manual CSV exports. Reduces audit-evidence gathering effort and brings Copilot activity into the standard pipeline alongside the rest of the org's logs.

Bad (vague, vendor-tone):

> Copilot got better at security. Worth checking out.

The "Why You Care" framing connects vendor-speak to **the org's actual operational reality**.

## Output surface

`vault/digests/weekly/YYYY-MM-DD-weekly-intelligence-digest.md` where `YYYY-MM-DD` is the run date (period_end).

## Composes with

All Phase-1 foundation skills via the runner. This skill itself is mostly config + framing.

## Acceptance test (for step 7 done-criteria)

One end-to-end run. Confirm:
- Digest file lands at the path above.
- All 5 sections present (TL;DR / What Changed / Why You Care / Detailed Findings / Sources).
- Tier badges render correctly.
- Failures from unverified sources appear in Sources (don't silently omit).
- `.state/weekly-intelligence-digest/seen.jsonl` populated.
- At least one source surfaces real items.
