---
name: adr-writer
description: Draft an Architecture Decision Record using the org's ADR template. ADRs document **technical decisions** with their context, the decision itself, and the consequences — focused on the "what" and "why" rather than implementation steps. Distinct from RFCs (which propose for discussion) and decision memos (which inform leadership). Output lands as a `decisions/` note in the vault. Use when capturing a technical architecture choice that's been made (or is about to be made) and needs to be discoverable + reviewable by future readers.
---

# adr-writer

Adapts the ADR pattern (Michael Nygard's original "any architecturally significant decision deserves a record") to the org's vault structure. Most architecturally significant decisions evaporate without an ADR; this skill makes capturing one cheap.

## When to use

- A technical decision has been made (sync vs async, batch vs stream, monolith vs microservice, KMS vs HSM for this case).
- A decision is about to be made and the author wants the ADR ready to ratify.
- Retroactively documenting a past decision discovered to be undocumented.

## When NOT to use

- Proposing a decision for org-wide discussion → `rfc-writer`.
- Informing leadership for an ask → `decision-memo-writer`.
- Quick decisions captured via the qc-decision template → [`quick-capture`](../quick-capture/SKILL.md).
- Control-exception decisions → [`exception-request-drafter`](../exception-request-drafter/SKILL.md).

## Document structure (org's ADR template)

```markdown
# ADR-{number} — {title}

**Status**: proposed | accepted | superseded | rejected
**Date**: YYYY-MM-DD
**Authors**: {names}
**Supersedes**: {[[adr-link]] if applicable}

## Context
{The forces at play. What problem are we solving? What constraints apply?}

## Decision
{The technical decision. Concise. Imperative voice — "we will use X" not "X might be a good choice".}

## Consequences
### Positive
- ...

### Negative / trade-offs
- ...

### Neutral
- ...

## Alternatives considered
### {Alt 1} — rejected because ...
### {Alt 2} — rejected because ...

## Related
- {[[wikilinks]] to related decisions, research notes, facts}
```

Lands at `vault/decisions/YYYY-MM-DD-adr-{slug}.md`.

## Composes with

- `vault-writer.write_decision` — final document writes through the standard pattern.
- `vault-querier` — find related ADRs to cite.
- `rfc-writer` — when an ADR's outcome would benefit from broader discussion first.

## Acceptance test (for step 32 done-criteria)

The 4 existing `decisions/` notes in the vault (Obsidian adoption, weekly-review cadence, Copilot exception rejection, the upcoming Q3 AI governance ADR) are the exemplar set. Live exercise included.
