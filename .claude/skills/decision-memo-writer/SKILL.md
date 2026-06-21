---
name: decision-memo-writer
description: Draft a one-page decision memo for leadership — options, recommendation, risks, asks. Distinct from ADRs (technical decisions, no exec ask) and RFCs (open-for-comment proposals). A decision memo is **terse**: 250-500 words, structured for someone with 5 minutes who needs to make or approve a decision. Output lands as an `insights/` note in the vault (because the memo informs but doesn't itself decide — the decision lives in a subsequent ADR). Use when an exec / sponsor / committee needs to make or ratify a decision.
---

# decision-memo-writer

The leadership-facing decision artifact. RFCs are for engineers; ADRs are for posterity; decision memos are for the person with 5 minutes to decide.

## When to use

- Bringing a decision to an exec / sponsor / committee for ratification.
- Pre-meeting brief: leader will see this before the meeting to come prepared.
- The strategic recommendation from `stakeholder-update-writer` exec tier needs a backing one-pager.

## When NOT to use

- Technical decision capture → `adr-writer`.
- Open-for-comment proposal → `rfc-writer`.
- Exception request → `exception-request-drafter`.
- Stakeholder update across many topics → `stakeholder-update-writer`.

## Document structure (one page, 250-500 words)

```markdown
# Decision Memo — {title}

**Decision needed**: {1 sentence — what the leader must decide}
**Decision-maker**: {role + name}
**Recommended decision**: {1 sentence — author's recommendation}
**Date**: YYYY-MM-DD
**Author / sponsor**: {names}

## Context (~60 words)
{What's the backdrop. Cite relevant vault notes.}

## Options
1. **{Option A}** — pros / cons / cost
2. **{Option B}** — pros / cons / cost
3. **{Option C — recommended}** — pros / cons / cost (+ why this one)

## Risk of inaction
{What happens if no decision is made? Cite the specific risk.}

## Asks
- Decision needed by: {date}
- If approved: {what unlocks immediately}
- If rejected: {what alternative path is needed}

## Sources
- {vault notes — research, facts, prior decisions}
```

Lands at `vault/insights/YYYY-MM-DD-decision-memo-{slug}.md` (it informs a decision; the decision itself becomes a separate `decisions/` ADR).

## Composes with

- `vault-querier` — pull supporting facts / research.
- `stakeholder-update-writer` — exec-tier outputs sometimes need decision-memo backup.
- `adr-writer` — once the decision is made, the ADR captures it.

## Acceptance test (for step 32 done-criteria)

One live decision memo. Natural fixture: the AI-governance position quarterly recommendation that needs a leader to choose between active/passive postures.
