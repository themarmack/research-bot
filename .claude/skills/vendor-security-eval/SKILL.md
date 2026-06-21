---
name: vendor-security-eval
description: Standardized security / risk evaluation of a dev or AI vendor against org policy — data flow diagram, SIG (Standardized Information Gathering) Lite/Full responses, SOC 2 Type 2 review, ISO 27001 review, model training opt-out terms, breach history (public + private disclosure), TPRM-file readiness scorecard. Produces a structured pre-procurement evaluation note the TPRM team can use as input to their formal process. Composes with ai-coding-tools-compare (broad comparison) and compliance-framework-lookup (specific control questions). Use before any new dev/AI vendor moves to formal TPRM intake.
---

# vendor-security-eval

The pre-TPRM-intake evaluation skill. Most dev / AI vendor decisions get stalled because the formal TPRM intake requires a complete information package that doesn't exist yet. This skill produces the package.

## When to use

- Pre-TPRM-intake: vendor identified as a candidate; need a structured information package.
- Re-evaluation: existing vendor's posture has materially changed (e.g., Cursor announces FedRAMP).
- Following an incident at a peer that uses the vendor.
- Annual TPRM-file refresh.

## When NOT to use

- General vendor comparison → `ai-coding-tools-compare`.
- The formal TPRM process itself — this skill produces input, doesn't replace.
- Vendor selection without a specific candidate identified.

## Evaluation rubric

### 1. Data flow

- Where does customer data flow? (Diagram + per-hop classification per `ai-tooling-data-flow-reviewer` pattern.)
- Are residency commitments contractual or best-effort?
- Data egress beyond the vendor (subprocessors)?

### 2. Standardized assessments

- **SIG Lite / SIG Full** — Shared Assessments Standardized Information Gathering responses. Required for TPRM intake.
- **SOC 2 Type 2** — current report obtained? Period covered?
- **ISO 27001** certification — current and in-scope for the service?
- **ISO 42001** alignment / certification (AI mgmt system) — emerging but worth asking.
- **FedRAMP Moderate / High** — if relevant (US gov adjacent).

### 3. AI-specific clauses (for AI vendors)

- **Training-data opt-out** — default? Contractual? Enforceable?
- **Model-routing transparency** — which models invoked when?
- **IP indemnity scope** — what's covered, what's excluded.
- **Content exclusion granularity** — org / repo / path-level.

### 4. Breach history

- **Public disclosures** — CVEs, SEC 8-K disclosures, named incidents.
- **CISA known-exploited list** entries.
- **Private disclosure track record** — coordinated disclosure responsiveness (per CERT/CC reports if available).

### 5. Sub-processors

- Cloud hosting (AWS / Azure / GCP / single-tenant on-prem).
- Embedded model providers.
- Other SaaS dependencies in the data path.

### 6. Contractual posture

- Notification SLAs for incidents.
- Data deletion on termination.
- Audit rights (right to audit, or pooled audit via SOC 2 reliance).
- Insurance carrying cyber coverage.

## Output structure

```markdown
# Vendor Security Evaluation — {vendor}

## Vendor summary
{1-paragraph}

## Per-section findings
[5 sections from rubric above]

## TPRM-readiness scorecard
- Information package complete? Y/N per artifact
- Net recommendation: advance-to-TPRM-intake / defer / reject

## Sources
{vendor docs + SIG responses + SOC report references}
```

Lands at `vault/research/vendor/YYYY-MM-DD-eval-{vendor-slug}.md`.

## Composes with

- `ai-coding-tools-compare` — broad-comparison side.
- `compliance-framework-lookup` — specific control questions.
- `ai-tooling-data-flow-reviewer` — for AI-vendor data-flow diagram.
- `vault-writer.write_research` — output.

## Acceptance test (for step 30 done-criteria)

One live vendor evaluation exercising all 6 rubric sections. Cursor is a natural candidate given the step-28 comparison's targeted-pilot recommendation.
