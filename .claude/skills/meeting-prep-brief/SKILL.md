---
name: meeting-prep-brief
description: Generate a one-page prep brief for a meeting from the user's notes + recent vault activity. Sections — meeting context, the participants (with their likely concerns, sourced from objection-response-library and people notes), the asks (what user needs to walk in prepared for), the prior context (relevant vault notes + decisions + facts), and the "if X comes up, here's the response" pre-empts. Use before any stakeholder meeting where the user wants to be ahead of the conversation rather than reacting to it.
---

# meeting-prep-brief

The pre-meeting deep-breath tool. Most stakeholder meetings could go better with 5 minutes of structured prep; this skill makes that prep cheap.

## When to use

- Pre-meeting prep (1-on-1 with a stakeholder, committee meeting, vendor sync).
- Pre-presentation prep (when a meeting is really a presentation + questions).
- After a meeting cancellation that gets rescheduled — generate a fresh brief rather than rely on memory.

## When NOT to use

- One-on-one meetings with peers where formality isn't needed.
- Meetings the user owns (they ARE the presenter — `demo-script-builder` or `enablement-content-creator` instead).

## Required inputs

- **Meeting topic** (1-2 sentences).
- **Participants** (names + roles).
- **The user's role in the meeting** (presenter / decision-maker / informer / listener).
- **The user's notes** (anything they typed about the meeting).
- **Decisions or action items expected**.

## Output structure

```markdown
# Meeting Prep — {topic} ({date})

## Context (2-3 sentences)
{Backdrop. Cite vault notes.}

## Participants + likely concerns
| Participant | Role | Likely concern (with [[objection-response]] reference) |
|-------------|------|--------------------------------------------------------|

## The user's asks
- {What the user needs from this meeting}

## Prior context (relevant vault notes)
- [[wikilinks to decisions / facts / research]]

## Pre-empts ("if X comes up, here's the response")
- {Topic A} → cite {canonical FAQ or objection response}
- {Topic B} → cite {vault fact}

## Walk-in checklist
- [ ] {one-liner reminder of key data point}
```

Lands at `vault/insights/YYYY-MM-DD-meeting-prep-{slug}.md`.

## Composes with

- `vault-querier` — pull recent vault activity + relevant facts.
- `objection-response-library` — anticipate concerns.
- `copilot-faq-answerer` — anticipate technical questions.
- `people-notes` in `vault/people/` — load known concerns of named participants.

## Acceptance test (for step 33 done-criteria)

One live meeting-prep brief exercising the structure. Natural fixture: the Payments AI governance kickoff scheduled to follow up on the rollout plan.
