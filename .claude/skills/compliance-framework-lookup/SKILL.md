---
name: compliance-framework-lookup
description: Cross-reference a specific control question against the org's relevant compliance frameworks — NIST 800-53 / 800-218 SSDF, PCI-DSS 4.0, SOX ITGC, ISO 27001 / 27034 / 42001, CIS Controls / Benchmarks, FFIEC IT Handbook. For a single question (e.g., "what's the relevant SOX ITGC control objective for AI-generated code in production?"), produces a side-by-side mapping showing which frameworks address it, which control IDs match, and where they conflict. Use when drafting policy that cites multiple frameworks, responding to an audit ask, or building a compensating-control matrix for an exception request.
---

# compliance-framework-lookup

The cross-framework triangulation tool. Bank policy typically claims alignment with multiple frameworks; this skill makes the mapping reproducible — for a single control question, show the row from each framework.

## When to use

- Drafting internal policy that needs framework-citation backing.
- Audit ask: "what control does X map to in NIST 800-53 vs PCI-DSS?"
- Building a compensating-control matrix for an `exception-request-drafter` document.
- Checking whether a new framework (e.g., ISO 42001) introduces new obligations the org's current control catalog doesn't cover.

## When NOT to use

- Regulator guidance (vs voluntary frameworks) → `financial-regulator-watch`.
- AI-governance-framework-specific deep-dive → `ai-governance-research`.
- The org's own internal control catalog lookup — that's an internal-systems integration question (still TBD per skills-plan open questions).

## Frameworks in scope

- **NIST 800-53** rev 5 — federal-grade security and privacy controls
- **NIST 800-218 SSDF** — Secure Software Development Framework
- **NIST AI RMF + GenAI Profile (600-1)** — see [`ai-governance-research`](../ai-governance-research/SKILL.md)
- **PCI-DSS 4.0** — card-data handling
- **SOX ITGC** — IT general controls for financial reporting
- **ISO 27001** — information security management system
- **ISO 27034** — application security
- **ISO 42001** — AI management system
- **CIS Controls v8** + **CIS Benchmarks** — implementation-level
- **FFIEC IT Handbook** — supervisory baseline
- **NYDFS Part 500** — NY cyber regulation

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the control question's key terms across `vault/research/compliance/**`, `vault/facts/{framework-entity}/**` (e.g. `nist-800-53`, `pci-dss`, `sox-itgc`, `iso-27001`), `vault/research/regulator/**` (regulator notes often cite the same controls), and recent `vault/digests/**` (last 90 days).
   - Backlink check on each in-scope framework's entity (e.g. `[[sox-itgc]]`, `[[nist-800-218]]`).
2. **Triage findings**:
   - If the vault already holds the cross-framework mapping for this question → return it with source citations (vault path + original source URLs). No new write.
   - If partial (some frameworks mapped, others not) → identify the **gap**. Web research targets only the unmapped frameworks.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: csrc.nist.gov (800-53, 800-218), PCI SSC document library, iso.org summaries, CIS Controls / Benchmarks pages, FFIEC IT Handbook, NYDFS Part 500 text.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - Framework text is tier-1 (no verification); any third-party crosswalk or interpretation of how control IDs map gets the full 3-vote treatment before it lands in the mapping table.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/compliance/YYYY-MM-DD-{question-slug}.md`
   - Frontmatter per `research.yml` schema: `topic: compliance-framework`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: the output structure below, with credibility-tier badges on every source.
6. **Stage promotable claims** to `_inbox/compliance-framework-lookup/`:
   - Any verified fact-typed claim (e.g. a stable control-ID mapping) → `_inbox/compliance-framework-lookup/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/{framework-entity}/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

## Output structure

```markdown
# Compliance Framework Lookup — {question}

## Question
{The specific control question}

## Cross-framework mapping
| Framework | Section / Control ID | Statement | Compliance-relevant nuance |

## Conflicts / gaps
{Where frameworks diverge or one is silent}

## Recommended policy citation
{Suggested framework + control to cite for the org's posture}

## Sources
```

Lands at `vault/research/compliance/YYYY-MM-DD-{question-slug}.md`.

## Composes with

- `ai-governance-research` — for the AI-specific frameworks.
- `financial-regulator-watch` — for the regulator-supervisory angle.
- `exception-request-drafter` — for the compensating-control matrix.

## Acceptance test (for step 29 done-criteria)

One lookup exercising at least 4 frameworks for a single question, with conflict / gap analysis.
