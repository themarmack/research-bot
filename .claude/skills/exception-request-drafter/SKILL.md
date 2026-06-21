---
name: exception-request-drafter
description: Draft a control-exception request that GRC / security architecture / model risk will actually accept. Covers any exception type — IaC guardrail override, secrets-rotation deferral, network-egress exception, license-deny-list adoption, AI tool config exception. Produces a structured document with: stated control + requested deviation, steel-manned risk being undertaken, compensating controls, expiry / renewal trigger, owner + sponsor, citations to underlying controls. Generalizes the `copilot-exception-handler` pattern from step 17 to all control exceptions. Use whenever a team needs to deviate from a documented control with documentation auditors will accept.
---

# exception-request-drafter

The exception-document factory. Most exception requests get rejected not because the underlying ask is unreasonable, but because the request lacks structure auditors recognize. This skill produces the structure.

## When to use

- A team needs to deviate from any documented control.
- A org-baseline finding from an ops-skill (`ghas-config-reviewer`, `iac-security-reviewer`, `secrets-hygiene-reviewer`, `secure-design-reviewer`) is being knowingly accepted rather than fixed.
- Renewing an existing exception that's at its sunset date.
- Drafting the rejection path for an exception that won't be granted (the rejection deserves the same documented structure).

## When NOT to use

- Copilot-specific exceptions → `copilot-exception-handler` (which calls this skill internally).
- Policy proposals (new controls, not deviations) → `rfc-writer` (planned step 32).
- Audit findings response → that's a different artifact.

## Required inputs

- **Stated control**: which control is being deviated from? Cite the control catalog entry.
- **Requested deviation**: precisely what's being changed.
- **Scope**: which systems / teams / time period.
- **Requestor + sponsor**: who's asking, who's accountable.
- **Justification narrative**: the requestor's case in their own words.
- **Proposed compensating controls**: what makes the residual risk acceptable.

## Structured document template

```markdown
# Exception Request — {requestor} — {short title}

## Decision: {Justified | Partially Justified | Not Justified — pending review}

## Control being deviated from
- **Control ID**: {org catalog entry, or external framework citation if no internal ID}
- **Control statement**: {what it requires}
- **Source**: {vault note, ops-skill finding ID, policy URL}

## Requested deviation
{Precisely what the requestor wants to do that the control would otherwise prohibit}

## Scope
- **Systems / services**: {list}
- **Teams / accounts**: {list}
- **Time period**: {start → end}

## Stated rationale (from requestor)
> {Verbatim or paraphrased}

## Risk being undertaken
{Steel-manned risk analysis — what could go wrong, what the impact would be, what data could be exposed, what controls would not catch the failure}

## Compensating controls
| Control | Implementation | Owner | Audit evidence |
|---------|----------------|-------|----------------|

## Decision rationale
{2-3 paragraphs citing the control statement, the requestor's case, and the org's actual posture from vault facts.}

## Renewal trigger
- {Calendar date OR event-based}
- **Review owner**: {name}

## Owner + sponsor
- **Requestor**: {name + role}
- **Sponsor**: {requestor's manager + role}
- **Approver**: {control owner / GRC partner}

## Citations
{vault notes, ops-skill findings, control catalog entries}
```

Output lands as a `decisions/` note: `vault/decisions/YYYY-MM-DD-exception-{slug}.md`.

## Composes with

- [`copilot-exception-handler`](../copilot-exception-handler/SKILL.md) — uses this internally for Copilot-specific exceptions.
- Any ops-skill finding becomes an exception draft when the team accepts rather than remediates.
- `vault-writer.write_decision` — final document goes through the standard decision pattern.

## Acceptance test (for step 27 done-criteria)

The template covers all 9 required sections; one live exercise produces a sample exception request (any non-Copilot case from the org's actual posture).
