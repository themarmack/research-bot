---
title: Inbox Promotion Rules
created: 2026-06-20
updated: 2026-06-20
tags: [meta]
source_skill: human
confidence: 3
links: [conventions]
---

# Inbox Promotion Rules

The `memory-curator` skill applies these rules when deciding what to do with notes that agents stage in `_inbox/{agent-id}/`.

Three possible verdicts per inbox item: **promote**, **patch**, **drop**.

## Promote — write a new durable note

A new note in a durable folder when ALL of the following hold:

- **Novel.** The claim/event/decision does not already exist as a durable note. Check via `vault-querier` for a matching `[[entity/predicate]]` or `[[slug]]`.
- **Specific.** The note answers a concrete question — "what is X's data handling policy" not "AI tools are evolving fast."
- **Future-useful.** The user will plausibly want to look this up again, or another skill will use it as input.
- **Sourced.** Has at least one `source_url` in frontmatter (or `source_skill: human` if user-authored). Unsourced agent claims → drop.
- **Surprise factor or load-bearing.** Either it changes the user's mental model, or it's referenced by other notes / decisions.

Default surface routing:
- Falsifiable typed claim about an entity → `facts/{entity}/{predicate}.md`
- Dated thing that happened → `events/YYYY-MM-DD/{slug}.md`
- A choice the user (or team) made → `decisions/YYYY-MM-DD-{slug}.md`
- A synthesis across multiple sources → `insights/{slug}.md`
- Output of a research run → `research/{topic}/YYYY-MM-DD-{slug}.md`
- Output of a scheduled agent → `digests/{cadence}/YYYY-MM-DD-{skill}.md`

## Patch — update an existing note

When the inbox item refers to an entity/topic with an existing durable note AND adds new information:

- Update the existing fact's `value` and bump `updated` and `confidence` if more sources now agree.
- Append a dated line to `events/YYYY-MM-DD/{slug}.md` if the same event has new details.
- Append to a research note's "Updates" section if the topic gained new findings.

Patching is preferred over creating a sibling note. Duplicate notes about the same `[[entity/predicate]]` are a smell.

## Drop — do nothing

Drop the inbox item (move to `_inbox/.dropped/` for audit) when:

- It's already known and unchanged.
- It's a marketing claim with no falsifiable substance.
- It's about identity/preferences/feedback (those belong in Tier-1 harness memory, not the vault).
- It contains content classified `#do-not-share` from an internal source the user didn't approve.
- Confidence is 1 ("tentative") AND no source URL.

**Guardrail (borrowed from OB1): never silently drop content with substance.** If the curator is uncertain whether something is droppable, leave it in `_inbox/` tagged `#needs-review` so a human can adjudicate. The audit trail in `_inbox/.dropped/` exists for the same reason — drops are reviewable, not destructive.

## Heuristics

- Default-drop in case of doubt for `digests/` items — digests are append-only history, not a wishlist.
- Default-promote for typed facts with at least one tier-1 source (per `source-registry` credibility tier).
- Never auto-promote anything tagged `#disputed` — those need human review.
