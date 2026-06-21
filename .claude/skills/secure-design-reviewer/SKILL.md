---
name: secure-design-reviewer
description: Critique a service / architecture design doc against the org's control objectives — data classification handling, key management, IAM (auth + authz), logging + monitoring, disaster recovery, third-party integrations, AI tool exposure. Produces a structured finding list per control category with `current_state` vs `expected_state`, severity, and remediation. Composes with threat-model-helper (threats identified there → controls validated here) and ai-tooling-data-flow-reviewer for the AI-specific data-flow dimension. Use during architecture review, before change-advisory-board approval, or when retrofitting a legacy service's design documentation.
---

# secure-design-reviewer

The control-side reviewer that complements [`threat-model-helper`](../threat-model-helper/SKILL.md). Where the threat model identifies what could go wrong, this skill identifies whether the architecture has the controls to prevent or detect it.

## When to use

- Architecture-review milestone (pre-CAB, pre-prod, retrospectively at audit prep).
- Retrofit: a legacy service's design doc has gone stale; validate against current standards.
- Companion review after `threat-model-helper`: do threats identified there have control coverage in the design?

## When NOT to use

- Code-level review → CodeQL.
- Workflow security → `actions-workflow-hardener`.
- AI-specific data-flow analysis → `ai-tooling-data-flow-reviewer` (planned).
- Generic threat modeling → `threat-model-helper`.

## Control categories

The skill checks each design doc against 7 categories. Each category has a checklist; missing items become findings.

### 1. Data classification + handling

- Is the data classified (public / internal / regulated / PII / PCI)?
- Are flows of regulated data documented (storage, transmission, processing)?
- Does the doc identify where data crosses trust boundaries?
- Is there a retention schedule per data class?
- Are exclusion patterns documented for AI tool context (Copilot content exclusions, etc.)?

### 2. Key management

- Are encryption keys identified (data-at-rest, data-in-transit, app-layer)?
- Is the KMS / HSM identified?
- Is key rotation schedule documented?
- Are emergency rotation procedures documented?

### 3. IAM (authentication + authorization)

- How does the service authenticate users? Workforce vs customer identities?
- Is SAML / OIDC the auth path?
- Is the authz model declared (RBAC / ABAC / per-resource)?
- Is least-privilege documented?
- Service-to-service auth (mTLS / OIDC / API keys)?

### 4. Logging + monitoring

- What's logged (user actions, system events, errors)?
- Are logs streamed to the SIEM?
- Is log retention documented (typically 90d hot, 1y warm, 7y cold for SOX)?
- Are logs free of secrets / PII (or masked)?
- Are anomaly alerts defined?

### 5. Disaster recovery

- RTO / RPO declared?
- Backup strategy documented?
- Failover tested in the design?
- Data sovereignty / cross-region replication considered?

### 6. Third-party integrations

- Each external dependency listed with vendor + TPRM file reference?
- Data flow to each third party explicit?
- Fallback if third party is unavailable?
- For AI tools specifically: per [[data-handling]] + [[data-residency-regions]] facts, is the org's tenant config understood?

### 7. AI tool exposure

- Does the service's data feed Copilot / any LLM context?
- Are content-exclusion patterns set for service-specific paths?
- Per [[security-prompt-injection-context]] objection — is content from this service prompt-injection-safe?
- Per [[skeptical-dev-data-leakage]] — is the service's data classification consistent with its AI tool exposure?

## Workflow

1. **Read the design doc**.
2. **Per category**: walk the checklist; identify covered + missing items.
3. **Cross-reference threat model** (if one exists for the service): for each threat identified, confirm the design has a mitigation control.
4. **Produce findings**: each missing or weak control becomes a finding with `current_state`, `expected_state`, severity, remediation, control-catalog reference.
5. **Summary**: counts per category, total findings, top-5 priority by severity.

## Output structure

```markdown
# Secure Design Review — {service name}

## Summary
- Total findings: {N}
- Critical: X | High: Y | Medium: Z | Low: W

## Top-5 priority remediations
1. ...

## Findings by category
### 1. Data classification + handling — {pass | gaps}
{findings}
### 2. Key management — ...
{...}

## Cross-reference: threat model
{If threat model exists, list each threat + whether design covers it}

## Sources
{vault notes, frameworks}
```

Lands at `vault/research/sdlc-best-practice/YYYY-MM-DD-design-review-{service-slug}.md`.

## Composes with

- [`threat-model-helper`](../threat-model-helper/SKILL.md) — natural pair.
- `vault-querier` — facts about Copilot data handling and similar AI-tool facts.
- `ai-tooling-data-flow-reviewer` (planned step 27) — the AI dimension.

## Acceptance test (for step 24 done-criteria)

One design review exercised against the same hypothetical service used for `threat-model-helper`'s acceptance. Confirm 7 categories covered, findings list with severity, cross-reference to threat model (if produced).
