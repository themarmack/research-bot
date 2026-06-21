---
name: copilot-exception-handler
description: Walk through a non-standard Copilot config request — public-code-filter-off, alternate model pin, content-exclusion-override, license-assignment outside the standard process — decide justified / partially justified / not justified, and produce the formal exception document with risk statement, compensating controls, expiry, owner, and renewal trigger. Pulls org constants from vault/facts/copilot/ and canonical answers from copilot-faq-answerer; pre-empts objector arguments via objection-response-library. Use whenever a team lead or developer submits a request that breaks the standard Copilot configuration.
---

# copilot-exception-handler

A Category 3 ops tool. Most exception requests are well-meaning misunderstandings of what the standard config protects against. A few are legitimate edge cases. This skill triages and produces the document that either denies cleanly (with a citation-backed explanation) or accepts conditionally (with compensating controls).

## When to use

- A team lead asks "can we turn off the public code filter for our team?"
- A developer asks "can I pin to a different model than the org default allows?"
- A repo owner asks "can we override org-level content exclusion for our repo?"
- A LOB head escalates a "Copilot rollout is taking too long because of [policy X]" complaint.

## When NOT to use

- A novel request without a canonical posture (no prior exception type) — research via `copilot-deep-dive` first.
- A request that's actually a feature ask, not a config exception — route to product feedback.
- A specific repo configuration question — that's `ghas-config-reviewer`.

## Decision matrix

For each exception type, the skill has a pre-decided posture:

| Exception type | Default verdict | Justification possible? |
|----------------|-----------------|------------------------|
| Public code filter off | **REJECT** | Almost never — strips IP indemnity (see [[ip-indemnity]] objection). |
| Content exclusion override (allow excluded paths) | **CASE-BY-CASE** | Only for repos with no regulated-data classification AND a strong velocity-blocked argument. |
| Pin to non-default model org-wide | **CASE-BY-CASE** | Possible for high-volume teams with documented model preference. |
| Pin to model NOT in the approved list | **REJECT** | Risks model-risk review of an unapproved model. |
| Use Copilot Chat from personal account on corp workstation | **REJECT** | Free-tier has different data handling per [[data-handling]] canonical. |
| Increase per-user license allocation beyond cohort | **CASE-BY-CASE** | Trivially approvable if budget allows. |
| Bypass training requirement | **REJECT** | Training is mandatory for the IP indemnity + SOX evidence story. |

## Required inputs

- **Requestor** (name, team, role).
- **Exception type** (from the matrix above; if none match, escalate).
- **Justification narrative** (the requestor's case in their own words).
- **Affected scope** (specific repos / users / time period).
- **Proposed compensating controls** if any.

## Workflow

1. **Classify** against the decision matrix.
2. **Pull the canonical answer** for the impacted concern via `copilot-faq-answerer` (e.g., a public-code-filter-off request triggers the IP indemnity entry).
3. **Pull the matching objection response** via `objection-response-library` for the steel-manned concern, and check whether the requestor's justification engages with that concern or sidesteps it.
4. **Decide**:
   - **Justified**: requestor's case has at least one of: (a) a regulatory carve-out the standard didn't anticipate, (b) a fact in `vault/facts/copilot/` more recent than the canonical, (c) a documented compensating control that mitigates the underlying risk.
   - **Partially justified**: justified for a constrained scope (specific repo, specific time window).
   - **Not justified**: write the citation-backed denial.
5. **Draft the document** in the format below.
6. **Schedule a renewal trigger** — exceptions sunset; the document records when to re-review.

## Output document structure

```markdown
# Copilot Exception Request — {requestor} — {exception_type}

## Decision: {Justified | Partially Justified | Not Justified}

## Request summary
- Requestor: {name, team, role}
- Type: {exception type}
- Scope: {specific scope}
- Justification narrative (from requestor):
> {narrative}

## Risk being undertaken (or denied)
{What changes if the exception is granted; cite the underlying canonical answer + objection response.}

## Compensating controls (if granted)
{Per-control specifics; reference internal control catalog entries where possible.}

## Decision rationale
{2-3 paragraphs citing the canonical answer, the objection response's steel-manned concern, and the org's vault facts.}

## Renewal trigger
{Calendar date OR event-based: "review on 2026-12-20" OR "review when OCC RFI on genAI publishes" OR "review at next AGENTS.md effectiveness check"}

## Owner
{Approver name; sponsor name (the requestor's manager).}

## Citations
- {facts referenced}
- {research notes}
- {canonical answers}
- {objection responses}
```

## Composes with

- [`copilot-faq-answerer`](../copilot-faq-answerer/SKILL.md) — canonical-answer citations.
- [`objection-response-library`](../objection-response-library/SKILL.md) — steel-manned-concern framing.
- `vault-querier` — load relevant facts.
- `vault-writer.write_decision` — final accepted/rejected document is itself a `decisions/` note in the vault.

## Acceptance test (for step 17 done-criteria)

Process one sample exception request (any from the decision matrix). Confirm:
- Document has all 7 sections.
- Risk statement cites at least one canonical answer or vault fact.
- Decision rationale cites the steel-manned concern from `objection-response-library`.
- Renewal trigger is set (date or event-based).
- Output lands as a `vault/decisions/YYYY-MM-DD-copilot-exception-{slug}.md` note.
