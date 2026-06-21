---
name: stakeholder-update-writer
description: Produce a tiered stakeholder update from raw progress notes + recent vault activity. Outputs three tiered versions in one go — exec (CIO/CISO/eng VP), eng lead (managers, principal engineers), IC (individual developers) — each tuned to that audience's decision authority, time budget, and what they actually need to act on. Composes on vault-querier (pulls last N days of digests/research/decisions for context), digest-writer's section conventions (TL;DR / What Changed), and the user's raw notes. Lands at vault/insights/YYYY-MM-DD-stakeholder-update-{slug}.md.
---

# stakeholder-update-writer

The single biggest reach multiplier for an SDLC program lead across a at-scale-dev org. One synthesis pass produces three audience-tuned updates — no more re-writing the same content for the CIO email, the eng-lead all-hands, and the IC newsletter.

## When to use

- End-of-week or end-of-month program update.
- Triggered by a notable event (regulator action, major Copilot release, incident response).
- Before a leadership review where you need exec-tier sign-off on something.
- Whenever the user says "I need to communicate this to {stakeholder}".

## When NOT to use

- Single-audience direct response (email back to one person) — write that directly.
- Verbatim transcripts / meeting minutes — different document type.
- Decision proposals — use `decision-memo-writer` (planned skill) or `quick-capture` for ADRs.

## Three tiers

### Exec tier (CIO, CISO, eng VP)

**Length**: ~150-250 words. Reads in 60 seconds.

**Focus**:
- What materially changed for the org.
- What decisions need exec sign-off in the next 1-4 weeks.
- Risk posture changes (regulator activity, supply-chain incidents, vendor announcements with audit/legal implications).
- Strategic direction shifts.

**Voice**: declarative, dense, single-syllable verbs. Quantified where possible. No vendor marketing language.

**Structure**:
- TL;DR (3 sentences)
- 1-3 decisions needed (with proposed answer + risk-if-not-decided)
- Risk + opportunity headline (one each)

### Eng lead tier (managers, principal engineers)

**Length**: ~400-600 words. Reads in 3-5 minutes.

**Focus**:
- Operational changes their teams should know about.
- Specific action items for their teams (one-week and one-month).
- What to communicate downward to ICs.
- Links to vault notes / research for deeper context.

**Voice**: explanatory but tight. Assumes domain literacy, doesn't assume operational omniscience.

**Structure**:
- TL;DR (4-5 bullets)
- What Changed (with [[wikilinks]] to vault research)
- What Your Teams Need to Do (this week / this month)
- Open Questions (for eng-lead-only conversations)

### IC tier (individual developers)

**Length**: ~300-500 words. Reads in 2-3 minutes.

**Focus**:
- What's changing in their day-to-day dev experience.
- What they need to do (concrete, low-friction).
- What they don't need to do (anti-pattern callouts).
- Where to ask questions.

**Voice**: friendly, practical, low jargon. Avoid corporate-speak. Use "you" not "ICs."

**Structure**:
- 3 bullets at top: "What's new", "What to do", "Where to ask"
- Per-topic: short paragraph + a "TL;DR" line
- A FAQ-style "Common questions" closer (often pulled from `copilot-faq-answerer` / `objection-response-library`)

## Workflow

1. **Read recent vault activity** via `vault-querier`:
   - Last 7-14 days of `vault/digests/`
   - Last 14-30 days of `vault/research/`
   - Any `vault/decisions/` with `status: accepted` or `proposed` in the window
   - Active `vault/projects/sdlc-modernization.md` open questions
2. **Read the user's raw notes** — anything they typed into the conversation about what to include.
3. **Cluster by topic** — same as `weekly-review`'s Themes pattern.
4. **Per-cluster, draft the 3 tiers** — exec / eng-lead / IC. Each tier sees the same underlying fact but with different framing, depth, and call-to-action.
5. **Apply the regulated-org lens** to exec tier — every item ties to SR 11-7 / FFIEC / OCC / SOX / NYDFS where applicable.
6. **Apply the practical-dev lens** to IC tier — explicit "what to do" and "what NOT to do".
7. **Write** to `vault/insights/YYYY-MM-DD-stakeholder-update-{slug}.md` as a single file with the three tiers as `##` sections.

## Output structure (one file, three tiers)

```markdown
# Stakeholder Update — {period} — {slug}

## Tier 1 — Exec (CIO / CISO / eng VP)
[150-250 words]

## Tier 2 — Eng Lead (managers / principal engineers)
[400-600 words]

## Tier 3 — IC (individual developers)
[300-500 words]
```

Each tier is a self-contained, sendable message — the user can copy / paste the relevant tier into the channel that matches the audience.

## Composes with

- `vault-querier` — pulls recent vault activity for context.
- `weekly-review` — sometimes the user starts a stakeholder update right after reading the weekly review.
- `copilot-faq-answerer` and `objection-response-library` — IC-tier "Common questions" content.
- `decision-memo-writer` (planned) — when a tier-1 exec ask is "we need a decision memo on X."

## Acceptance test (for step 15 done-criteria)

Generate one stakeholder update from the past week of vault activity. Confirm:
- File at `vault/insights/YYYY-MM-DD-stakeholder-update-{slug}.md` with all 3 tiered `##` sections.
- Exec tier: ≤250 words, includes 1-3 decisions needed.
- Eng lead tier: 400-600 words with `[[wikilinks]]` to vault research.
- IC tier: 300-500 words with concrete what-to-do guidance.
- Each tier is self-contained (a stakeholder reading their tier doesn't need to read the others).
