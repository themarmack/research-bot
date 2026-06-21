---
name: rfc-writer
description: Draft a Request for Comments document — a structured proposal for an org-wide change that needs review and discussion before becoming a decision. RFCs go further than ADRs because they propose (not declare) and emphasize the rollout, rollback, risk, and migration mechanics that org-wide changes require. Distinct from ADRs (technical decisions) and decision memos (leadership-facing asks). Output lands as a `decisions/` note with status `proposed`. Use when proposing a change that affects more than one team and requires comment + revision before commitment.
---

# rfc-writer

The pre-decision proposal document. ADRs declare; RFCs propose for discussion. Use when the change is large enough that pre-commitment review is the right shape.

## When to use

- Proposing an org-wide platform / process / standard change (e.g., the Actions hardening campaign).
- A new policy proposal (e.g., the AI governance position).
- A planned deprecation that affects more than one team.
- A material change to a shared service.

## When NOT to use

- Decision already made → `adr-writer`.
- One-paragraph stakeholder ask → use the `stakeholder-update-writer` decisions-needed section.
- Control exceptions → `exception-request-drafter`.

## Document structure

```markdown
# RFC-{number} — {title}

**Status**: draft | open-for-comment | accepted | rejected | superseded
**Author**: {name}
**Sponsor**: {executive sponsor}
**Comment period**: {open → close dates}
**Date**: YYYY-MM-DD

## Summary
{2-3 sentences. What is being proposed?}

## Motivation
{Why now? What problem are we solving? Cite relevant vault notes.}

## Proposal
{The concrete change. Include design diagrams if architectural.}

## Rollout plan
{Phased plan with timing. Phase 1 / Phase 2 / Phase 3. Cohorts. Criteria for moving between phases.}

## Rollback plan
{How do we reverse if the change goes badly? What's the trigger for rollback?}

## Risk
{What could go wrong? Likelihood + impact + mitigation per risk.}

## Migration
{If this replaces an existing system / process, what's the migration path? Cohorts? Cutover?}

## Open questions
{Items requiring decision before the RFC can ratify.}

## Alternatives considered
{Options that didn't make the proposal — and why.}

## Related
{[[wikilinks]] — research notes, prior decisions, facts.}
```

Lands at `vault/decisions/YYYY-MM-DD-rfc-{slug}.md` initially with `status: draft`; transitions to `open-for-comment`, then `accepted` / `rejected` / `superseded`.

## Composes with

- `vault-writer.write_decision`.
- `stakeholder-update-writer` — open-for-comment RFCs feature in the eng-lead-tier updates.
- `adr-writer` — accepted RFCs may spawn ADRs that capture the resulting technical decisions.

## Acceptance test (for step 32 done-criteria)

SKILL.md describes the 9-section RFC template and the status lifecycle. Live exercise deferred — the next genuine org-wide proposal is the natural trigger.
