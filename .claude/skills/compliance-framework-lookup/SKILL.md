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

## Obsidian-first workflow

Same Phase-1 pattern. Output topic: `compliance-framework`. Vault facts under `vault/facts/{framework-entity}/`.

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
