---
name: learning-capture
description: Save a structured insight note from an article, conversation, or experience. Routes through vault-writer to vault/insights/ (or vault/facts/{entity}/{predicate}.md if the captured content is atomic and falsifiable). Uses the controlled tag vocabulary. Distinct from quick-capture (which uses the qc-* sentence-starter formats and is faster). Use whenever encountering content worth retaining beyond the current conversation — a blog post that changes your mental model, a learning from a meeting that should outlast the meeting, a synthesis across multiple sources.
---

# learning-capture

The Category 6 PKM skill for "this is worth keeping." Distinct from `quick-capture` (which uses sentence-starter formats for fast turnaround) — `learning-capture` allows fuller framing when the input deserves it.

## When to use

- An article / talk / conversation changes a mental model.
- A synthesis across multiple inputs is worth keeping as a single insight.
- A "learnings from X" output that needs more structure than `qc-insight` provides.

## When NOT to use

- One-line capture → `quick-capture` (qc-insight format).
- Multi-source research → Category 1 researcher skills.
- Durable typed fact → write through `vault-writer.write_fact` directly.

## Workflow

1. **Input**: source description + the learning itself + the trigger.
2. **Classify**: is it an insight (synthesis-shaped) or a fact (entity/predicate-shaped)?
3. **Write** via `vault-writer.write_insight` or `write_fact` accordingly.
4. **Tag** from the controlled vocabulary in `_meta/tags.md`.
5. **Link** to related vault notes via `vault-querier` for backlinks.

## Output

`vault/insights/YYYY-MM-DD-{slug}.md` OR `vault/facts/{entity}/{predicate}.md`.

## Composes with

- `vault-writer` — actual write.
- `vault-querier` — suggest related notes for `[[wikilinks]]`.
- `memory-curator` — when uncertain whether durable.

## Acceptance test

SKILL.md describes the classification logic. Live exercise deferred to next learning capture.
