---
name: reading-queue-summarizer
description: Triage and summarize a backlog of saved articles / papers. For each item — 1-paragraph summary, salient quotes, vault connections, and a verdict (promote to a research note / capture as an insight / dismiss / defer). Especially useful after a busy intelligence-digest week when the user has marked items for follow-up reading. Output at vault/insights/YYYY-MM-DD-reading-triage-{slug}.md plus per-item promotion notes where applicable.
---

# reading-queue-summarizer

The backlog-clearing skill. Reading queues become coffin lists; this skill triages efficiently and produces durable artifacts only for items that earn them.

## When to use

- Weekly clear-down of a saved-article backlog.
- After a busy intelligence-digest week with many marked items.
- Pre-vacation triage to avoid coming back to a 50-item queue.

## Per-item verdict

- **PROMOTE**: worth a full research note (route to relevant Category 1 researcher).
- **CAPTURE**: 1-2 sentence insight worth keeping (`learning-capture` or `quick-capture`).
- **DISMISS**: doesn't merit retention; move on.
- **DEFER**: not now, but flag for re-triage in N days.

## Output structure

```markdown
# Reading Triage — {date}

## Summary
- N items triaged: P promoted / C captured / D dismissed / F deferred

## Per item
### {item title}
- Source: {URL}
- 1-paragraph summary
- Salient quote
- Vault connections: [[wikilinks]]
- Verdict: PROMOTE / CAPTURE / DISMISS / DEFER
- Action: {if PROMOTE: which researcher; if CAPTURE: what to capture}
```

Lands at `vault/insights/YYYY-MM-DD-reading-triage-{slug}.md`.

## Acceptance test

SKILL.md describes the 4-verdict framework. Live exercise deferred.
