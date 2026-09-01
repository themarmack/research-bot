---
name: financial-regulator-watch
description: On-demand Category 1 researcher targeting US (and EU/UK) financial regulators for guidance touching software risk, AI/ML, third-party risk, cyber, and SDLC modernization. Sources: OCC (bulletins, SR letters), Federal Reserve (SR letters, supervisory guidance), FDIC, FFIEC (IT Handbook, joint statements), SEC, FINRA, CFPB, NYDFS (Part 500), FCA, ECB. Enforces Obsidian-first contract. Outputs at vault/research/regulator/YYYY-MM-DD-{slug}.md; verified guidance items get staged for memory-curator promotion to vault/facts/{regulator-entity}/. Use when the user asks an on-demand question about a specific financial regulator's guidance or expectations — producing a fresh, cited research note — not the scheduled monthly regulator sweep (monthly-regulator-watch), voluntary-framework control mapping (compliance-framework-lookup), or AI-governance frameworks (ai-governance-research).
---

# financial-regulator-watch

The differentiator skill. Most SDLC research is vendor-neutral / industry-generic; this one is calibrated for **the regulator's lens** — what does the OCC actually expect, what's the current FFIEC IT Handbook saying, where's the SEC headed on AI governance.

## When to use

- A specific regulatory question: "Has the OCC issued guidance on Copilot specifically?" "What does NYDFS 500 say about AI dev tooling?" "FFIEC IT Handbook — Section X update?"
- Stakeholder ask: legal, compliance, or audit wants documented sourcing for a control objective.
- Background research before a decision that has audit visibility.

## When NOT to use

- General compliance framework lookup (NIST CSF, ISO 27001) → [`compliance-framework-lookup`](../compliance-framework-lookup/SKILL.md).
- AI-specific governance (NIST AI RMF, EU AI Act) → `ai-governance-research`.
- Internal control catalog questions — that's an internal-systems integration question, defer until decided.

## Source taxonomy

Tier-1 primary sources by regulator:

| Regulator | Primary surface | Frequency |
|-----------|-----------------|-----------|
| OCC | Bulletins, supervisory guidance, semiannual risk perspective | weekly |
| Federal Reserve | SR letters, supervisory guidance, FOMC (rarely relevant) | weekly |
| FDIC | Financial Institution Letters | weekly |
| FFIEC | IT Handbook (chapters, esp. WPK, Operations, AIO), joint statements | quarterly |
| SEC | Risk alerts, OCIE bulletins, AI-specific releases | monthly |
| FINRA | Regulatory notices | monthly |
| CFPB | Circulars (esp. AI/algorithmic discrimination) | monthly |
| NYDFS | Part 500 updates, industry letters, AI-specific guidance | monthly |
| FCA (UK) | Discussion papers, policy statements | quarterly |
| ECB (EU) | TRIM, ICT-risk guidelines, DORA-related | quarterly |

Where source-registry has the regulator's feed, use it. Where not, target the regulator's specific bulletins/press page.

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the question's key terms across `vault/facts/{regulator-entity}/**` (e.g. `occ`, `ffiec`, `nydfs`), `vault/research/regulator/**`, and recent regulator-tagged `vault/digests/**` (last 90 days — `monthly-regulator-watch` output lands there).
   - Backlink check on the regulator's entity (e.g. `[[occ]]`, `[[nydfs-500]]`) and the question's other entities.
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs from the fact's frontmatter). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`), prioritizing the primary regulator surfaces in the source taxonomy above (bulletins, SR letters, FILs, handbook chapters). Where `source-registry` has the regulator's feed, use it; where not, target the regulator's bulletins/press page.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - Regulator press text itself is tier-1 (no verification), but third-party interpretations of what the press *means* get the full 3-vote treatment.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/regulator/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic` from the taxonomy below, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/financial-regulator-watch/`:
   - Any verified fact-typed guidance item → `_inbox/financial-regulator-watch/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/{regulator-entity}/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

## Topic taxonomy

For the research note's `topic` field, use:
- `occ` / `frb` / `fdic` / `ffiec` / `sec` / `finra` / `cfpb` / `nydfs` / `fca` / `ecb` — single-regulator deep dives
- `joint-guidance` — when multiple regulators issued the same/joint statement
- `cross-regulator-comparison` — comparing posture across regulators on a topic

## Compliance-relevant framing

The framing isn't an add-on for this skill — it's the whole point. Every finding ties to a specific org operational reality: which control does this map to in your existing control catalog, what control objective does it strengthen or weaken, what's the audit-evidence implication, when does the requirement take effect.

## Composes with

The Phase-1 foundation named in the workflow above (`vault-querier`, `source-fetcher` + `prompt-injection-guard`, `claim-extractor` + `verify-claim`, `digest-writer` → `vault-writer`, `_inbox/` + `memory-curator`).

- [`executive-summary-writer`](../executive-summary-writer/SKILL.md) — **only when the user explicitly asks for an exec summary** (never auto-invoked after vault write). Takes the just-written research note's path and produces a 1-page summary tuned to a named audience (CISO, VP Eng, etc.).
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 12 done-criteria)

One live end-to-end research run produces a note at `vault/research/regulator/YYYY-MM-DD-{slug}.md` with tier-1 source citations and explicit org-control-catalog mapping.
