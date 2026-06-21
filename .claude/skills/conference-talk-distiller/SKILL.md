---
name: conference-talk-distiller
description: Turn a conference talk's slides / transcript / recording into the 3 things that matter for the user's program. Most talks have 1-3 substantive ideas wrapped in 30-45 minutes; this skill extracts the substance. Output at vault/insights/YYYY-MM-DD-talk-{slug}.md with the 3 key ideas + compliance-relevant takeaways + speaker recommendations to track. Use after attending or watching a recorded talk that the user wants to retain value from.
---

# conference-talk-distiller

The talk-recap skill. Most conference talks have rich ideas buried in narrative; the user doesn't have time to re-watch but wants the substance retained.

## When to use

- After watching a recorded talk.
- After attending a live talk where the user took rough notes.
- When the `conference-cfp-and-recap-watch` (step 23) digest flags a talk worth distilling.

## When NOT to use

- Full conference recap → `conference-cfp-and-recap-watch`.
- Multiple talks at once → run this skill per talk.

## Distillation framework

For each talk, identify:

1. **The thesis** — 1-2 sentences. What is the speaker really arguing?
2. **The 3 things that matter for our program** — compliance-relevant takeaways.
3. **The mental-model shift** (if any) — does this change how we think about something?
4. **Speaker worth tracking** — does this person belong in `voices.csv`?
5. **What I'd ask in Q&A** — articulating questions sharpens thinking.

## Output structure

```markdown
# Talk Distillation — {speaker} — {title} ({conference})

## Thesis
{1-2 sentences}

## 3 things that matter for our program
1. ...

## Mental-model shift (if any)
{...}

## Speaker
- Worth adding to voices.csv? {yes/no + reason}
- Other surfaces (Substack, GitHub, etc.)

## What I'd ask in Q&A
- ...

## Related vault notes
- [[wikilinks]]
```

Lands at `vault/insights/YYYY-MM-DD-talk-{slug}.md`.

## Composes with

- `conference-cfp-and-recap-watch` — surfaces talks worth distilling.
- `voices-roster-curator` — when a speaker becomes a voice worth tracking.
- `vault-querier` — find related vault context.

## Acceptance test

SKILL.md describes the 5-element framework. Live exercise deferred.
