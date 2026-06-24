---
name: financial-regulator-watch
description: On-demand Category 1 researcher targeting US (and EU/UK) financial regulators for guidance touching software risk, AI/ML, third-party risk, cyber, and SDLC modernization. Sources: OCC (bulletins, SR letters), Federal Reserve (SR letters, supervisory guidance), FDIC, FFIEC (IT Handbook, joint statements), SEC, FINRA, CFPB, NYDFS (Part 500), FCA, ECB. Enforces Obsidian-first contract. Outputs at vault/research/regulator/YYYY-MM-DD-{slug}.md; verified guidance items get staged for memory-curator promotion to vault/facts/{regulator-entity}/.
---

# financial-regulator-watch

The differentiator skill. Most SDLC research is vendor-neutral / industry-generic; this one is calibrated for **the regulator's lens** — what does the OCC actually expect, what's the current FFIEC IT Handbook saying, where's the SEC headed on AI governance.

## When to use

- A specific regulatory question: "Has the OCC issued guidance on Copilot specifically?" "What does NYDFS 500 say about AI dev tooling?" "FFIEC IT Handbook — Section X update?"
- Stakeholder ask: legal, compliance, or audit wants documented sourcing for a control objective.
- Background research before a decision that has audit visibility.

## When NOT to use

- General compliance framework lookup (NIST CSF, ISO 27001) → `compliance-framework-lookup` (planned).
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

## Obsidian-first workflow

Same as the other Category 1 researchers (see [`copilot-deep-dive`](../copilot-deep-dive/SKILL.md)):
1. Query `vault/facts/{regulator-entity}/**`, `vault/research/regulator/**`, recent regulator-tagged `vault/digests/**` first.
2. Identify gap.
3. Web research only on the gap, prioritizing primary regulator sources.
4. Verify any *interpretive* claim via `verify-claim` — regulator press text itself is tier-1 (no verification), but third-party interpretations of what the press *means* get the 3-vote treatment.
5. Write research note to `vault/research/regulator/YYYY-MM-DD-{slug}.md`.
6. Stage promotable facts to `_inbox/financial-regulator-watch/`.

## Topic taxonomy

For the research note's `topic` field, use:
- `occ` / `frb` / `fdic` / `ffiec` / `sec` / `finra` / `cfpb` / `nydfs` / `fca` / `ecb` — single-regulator deep dives
- `joint-guidance` — when multiple regulators issued the same/joint statement
- `cross-regulator-comparison` — comparing posture across regulators on a topic

## Compliance-relevant framing

The framing isn't an add-on for this skill — it's the whole point. Every finding ties to a specific org operational reality: which control does this map to in your existing control catalog, what control objective does it strengthen or weaken, what's the audit-evidence implication, when does the requirement take effect.

## Composes with

Same Phase-1 foundation as other Category 1 researchers.

- [`executive-summary-writer`](../executive-summary-writer/SKILL.md) — **only when the user explicitly asks for an exec summary** (never auto-invoked after vault write). Takes the just-written research note's path and produces a 1-page summary tuned to a named audience (CISO, VP Eng, etc.).
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 12 done-criteria)

One live end-to-end research run produces a note at `vault/research/regulator/YYYY-MM-DD-{slug}.md` with tier-1 source citations and explicit org-control-catalog mapping.
