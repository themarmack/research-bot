---
name: reading-queue-summarizer
description: Triage and summarize a backlog of saved articles / papers. For each item — 1-paragraph summary, salient quotes, vault connections, and a verdict (promote to a research note / capture as an insight / dismiss / defer). Especially useful after a busy intelligence-digest week when the user has marked items for follow-up reading. Output at vault/insights/YYYY-MM-DD-reading-triage-{slug}.md plus per-item promotion notes where applicable. Use when the user asks to triage, clear, or summarize their reading queue, saved articles, or marked follow-up items.
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

As the final step, write the triage note via `vault-writer.write_insight` to `vault/insights/YYYY-MM-DD-reading-triage-{slug}.md` — the verdicts and defer dates are only useful if they persist. PROMOTE and CAPTURE actions then route through the named researcher or `learning-capture` / `quick-capture` respectively.

## Composes with

- `vault-querier` — find vault connections per item.
- `vault-writer.write_insight` — persists the triage note (final step).
- `learning-capture` / `quick-capture` — CAPTURE-verdict items.
- Category 1 researchers — PROMOTE-verdict items.

## Acceptance test

SKILL.md describes the 4-verdict framework. Live exercise deferred.
