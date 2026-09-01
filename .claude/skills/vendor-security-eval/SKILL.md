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

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the vendor's name across `vault/research/vendor/**` (prior evaluations — e.g. [[2026-06-20-eval-cursor]]), `vault/research/ai-coding-tools/**` (comparison notes carry per-vendor rubric rows), `vault/facts/{vendor-entity}/**`, and recent `vault/digests/**` (last 90 days — vendor posture changes often surface there first).
   - Backlink check on the vendor's entity (e.g. `[[cursor]]`, `[[anthropic]]`).
2. **Triage findings**:
   - If a current evaluation already exists → return it with source citations (vault path + original source URLs). No new write.
   - If partial (e.g. some rubric sections covered, or the posture has materially changed since) → identify the **gap**. Web research targets only the gap sections.
   - If empty → full evaluation.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: the vendor's trust center / security docs / subprocessor list, SOC 2 and ISO certificate registries, SEC EDGAR (8-K breach disclosures), CISA KEV catalog.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - A vendor's certifications and contractual terms are tier-1 from the vendor's own trust pages; breach-history claims, "in practice" posture claims, and anything sourced from commentary get the full 3-vote treatment before landing in the scorecard.
5. **Work the 6-section rubric below**, filling each section from vault facts first, verified web claims second.
6. **Write the evaluation note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/vendor/YYYY-MM-DD-eval-{vendor-slug}.md`
   - Frontmatter per `research.yml` schema: `topic: vendor`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: the output structure below, with credibility-tier badges on every source.
7. **Stage promotable claims** to `_inbox/vendor-security-eval/`:
   - Any verified fact-typed claim (e.g. "vendor X holds SOC 2 Type 2 through {date}") → `_inbox/vendor-security-eval/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/{vendor-entity}/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

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
- `digest-writer` → `vault-writer.write_research` — output.

## Acceptance test (for step 30 done-criteria)

One live vendor evaluation exercising all 6 rubric sections. Cursor is a natural candidate given the step-28 comparison's targeted-pilot recommendation.
