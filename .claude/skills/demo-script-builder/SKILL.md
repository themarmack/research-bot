---
name: demo-script-builder
description: Build a tailored demo script for an AI-coding / SDLC-modernization audience. Inputs — audience type (skeptical dev / curious leader / risk-focused auditor / vendor evaluator), demo goal (familiarization / objection-handling / specific-feature showcase / posture demonstration), time budget (10 / 20 / 45 minutes). Output is a moment-by-moment script with prep checklist, the specific Copilot prompts / commands the demoer will type, expected output narration, and the fallback plan if a step fails live. Use when prepping for a stakeholder demo, audit conversation, vendor-account-team meeting, or all-hands familiarization.
---

# demo-script-builder

The "demo doesn't crash live" insurance policy. AI-coding demos especially go off-rails when the model produces something unexpected; this skill builds the runbook that makes the demo land regardless.

## When to use

- Stakeholder demo (executive, peer team, audit team).
- Vendor-account-team demo prep.
- All-hands familiarization for a cohort.
- Conference talk demo segment.

## When NOT to use

- General training content → `enablement-content-creator`.
- Vendor evaluation that's research-shaped → `vendor-security-eval`.

## Required inputs

- **Audience type**: skeptical dev / curious leader / risk-focused auditor / vendor evaluator.
- **Demo goal**: familiarization / objection-handling / specific-feature showcase / posture demonstration.
- **Time budget**: 10 / 20 / 45 minutes.
- **Demo environment**: live Copilot in IDE / sandbox repo / staged screen recording.
- **Audience prior knowledge**: minimal / moderate / expert.

## Output structure

```markdown
# Demo Script — {goal} for {audience type} ({time budget})

## Prep checklist (T-30 minutes)
- [ ] ...

## Opening (T+0 — 2 minutes)
- One-line setup
- Audience expectations check

## Beat 1: {beat title} (3-7 minutes)
- **What you say**: {narration}
- **What you do**: {specific Copilot prompt or command to type}
- **Expected output**: {what should appear}
- **Fallback if model produces unexpected output**: {plan}
- **Address-the-skeptic line**: {pre-empt the likely objection}

## Beat 2 ... Beat N

## Closing (last 2-3 minutes)
- The takeaway sentence
- Q&A prompt

## Common questions + responses (cite objection-response-library)
- {Q1}: pull from {canonical objection}
- ...
```

Lands at `vault/insights/YYYY-MM-DD-demo-script-{goal}-{audience}.md`.

## Composes with

- `copilot-faq-answerer` + `objection-response-library` — the question/objection responses anticipated.
- `vault-querier` — relevant facts to anchor the demo.

## Acceptance test (for step 33 done-criteria)

SKILL.md covers the moment-by-moment structure with fallback plans. Live exercise deferred to first actual demo prep.
