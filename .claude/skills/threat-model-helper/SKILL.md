---
name: threat-model-helper
description: Generate a STRIDE threat model (or LINDDUN for privacy-focused services) from a service description — components, data flows, trust boundaries. Pre-loaded with a compliance-relevant threat catalog: regulated-data exfiltration, third-party AI tool egress, prompt injection from upstream content, Mini-Shai-Hulud-class CI/CD compromise, model output as control bypass, SR 11-7-adjacent model-input risks. Each threat carries a likelihood + impact + recommended control mapped to the org's control catalog. Use during architecture review, before a new service goes through change-management, or when retrofitting threat models for legacy services.
---

# threat-model-helper

The org's first-pass threat-modeling tool. Most services in a regulated organization's portfolio either lack a threat model entirely or have one frozen from initial design. This skill makes "generate a fresh STRIDE pass" cheap enough to do at any milestone.

## When to use

- New service entering architecture review.
- Retrofit for a service that has no threat model on file.
- Re-threat-model after a material change (new dependency, new data flow, new integration with an AI tool).
- Pre-incident-response prep: think through what could go wrong before it does.

## When NOT to use

- Code-level vulnerability hunting → `codeql-pattern-finder` or `iac-security-reviewer`.
- Single-control review → `secure-design-reviewer` for architecture doc; `actions-workflow-hardener` for workflows.
- Compliance gap analysis → `compliance-framework-lookup` (planned).

## Compliance-relevant threat catalog (pre-loaded)

For each new service, the skill walks through these threat families, scoring whether each applies + at what likelihood:

| Family | Description | Default applicability |
|--------|-------------|----------------------|
| S — Spoofing | Identity forgery | medium baseline |
| T — Tampering | Data integrity violation | medium baseline |
| R — Repudiation | Lack of audit trail / non-repudiation | high baseline (SOX evidence) |
| I — Information disclosure | Regulated-data exfiltration | **HIGH baseline** for any service touching customer/card data |
| D — Denial of service | Availability impact | medium baseline |
| E — Elevation of privilege | Auth bypass / privilege escalation | medium baseline |

Plus **org-specific threat families** layered on STRIDE:

| Bank-specific family | Description | When applicable |
|----------------------|-------------|-----------------|
| Regulated-data egress | Data leaving the org's boundary via AI tool / 3rd-party / log | Any service where Copilot, Cursor, etc. could see the data |
| Prompt injection from upstream | Untrusted content reaching an LLM context | Any service whose data feeds Copilot Chat / knowledge bases / RAG |
| CI/CD supply-chain | Mini-Shai-Hulud-class workflow compromise | Any service with non-trivial CI |
| Model output as control bypass | Using an LLM to make a decision that should be policy-enforced | Any service where AI generates user-facing decisions |
| Audit-trail completeness | Per [[audit-per-suggestion-traceability]] objection — what's the per-event evidence trail? | Any SOX-relevant service |

## Required inputs

- **Service description**: 3-5 sentences on what it does.
- **Component diagram** (text or ASCII OK): components + data stores + external integrations.
- **Data flows**: which data moves between which components.
- **Trust boundaries**: explicit boundary lines (network, identity, data-classification).
- **Data classification**: regulated? PII? card data? PHI? public?
- **AI tool integration**: does Copilot / any LLM see the data?

## Workflow

1. Walk through each STRIDE letter; for each, score applicability HIGH/MEDIUM/LOW given the service description.
2. Walk through each org-specific family; same scoring.
3. For HIGH and MEDIUM threats, produce a concrete attack scenario + recommended control mapped to the org's control catalog (or external standard if internal catalog isn't named in the input).
4. Highlight the **top 5 threats by likelihood × impact** at the top.
5. Note **out-of-scope but adjacent threats** (e.g., the service doesn't touch X but neighbor service does).

## Output structure

```markdown
# Threat Model — {service name}

## Service summary
{1-paragraph description}

## Top 5 threats (likelihood × impact)
1. ...

## STRIDE table
| Threat | Likelihood | Impact | Scenario | Control |
|--------|-----------|--------|----------|---------|

## Bank-specific threat families
[same table shape]

## Out-of-scope but adjacent
- {one-liners}

## Sources
{linked vault notes, frameworks referenced}
```

Lands at `vault/research/sdlc-best-practice/YYYY-MM-DD-threat-model-{service-slug}.md` (or topic depending on service domain).

## Composes with

- [`secure-design-reviewer`](../secure-design-reviewer/SKILL.md) — natural pair; threat model identifies risks, design review checks if architecture mitigates them.
- [`ai-tooling-data-flow-reviewer`](../ai-tooling-data-flow-reviewer/SKILL.md) (planned step 27) — for AI-integration-specific data-flow concerns.
- `vault-querier` — pull related vault notes (existing facts about AI tool data handling, supply-chain attack patterns).

## Acceptance test (for step 24 done-criteria)

One threat model exercised against a hypothetical service description. Confirm: STRIDE table populated, org-specific families layered on top, top-5 ordered by likelihood × impact, controls mapped (named control or external framework reference).
