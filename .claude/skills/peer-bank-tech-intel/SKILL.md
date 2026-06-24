---
name: peer-bank-tech-intel
description: Collect what other major banks publicly share about their developer platforms, AI coding adoption, platform engineering, and SDLC modernization — engineering blogs (JPMorgan, Goldman Sachs, Morgan Stanley, Capital One, BofA, Wells Fargo, Citi, HSBC, Deutsche Bank, Barclays), conference talks (FS-ISAC, QCon Financial Services tracks), public RFCs / open-source projects, and named-analyst commentary. Output at vault/research/peer-bank/YYYY-MM-DD-{slug}.md. Composes with stakeholder-update-writer (exec asks "what are peers doing?") and decision-memo-writer.
---

# peer-bank-tech-intel

The "what are peers actually doing?" skill. Banks rarely share details publicly, but enough information leaks through engineering blogs, conference talks, public open-source contributions, and named-analyst case studies to triangulate posture.

## When to use

- Exec or board question: "what are JPMorgan / Goldman / etc. doing on AI coding?"
- Posture review: is the bank ahead, on pace, or behind peers on a specific capability?
- Vendor selection: which peers have publicly adopted vendor X — and what did they say afterward?
- Annual peer-bank posture summary.

## When NOT to use

- Specific vendor evaluation → `vendor-security-eval`.
- Specific Copilot question → `copilot-faq-answerer`.
- Confidential / non-public peer intelligence — out of scope, do not source from non-public material.

## Source taxonomy

- **Engineering blogs**: medium.com, eng blog subdomains for the named banks above.
- **Conference talks**: QCon, GOTO, KubeCon (financial-services track when present), GitHub Universe, FS-ISAC summits, BankInfoSecurity webinars.
- **Open-source contributions**: github.com/{bank-org}, Bank-org publicly-contributed CodeQL packs, CloudCustodian policies, etc.
- **Named-analyst case studies**: Forrester Wave entries, Gartner peer insights, public IDC reports (where excerpts are public).
- **Earnings-call quotes**: tech-specific quotes from quarterly earnings calls (public materials).

## Bank-relevant framing per finding

Each finding answers:
1. What did the peer publicly say or show?
2. How does the org's posture compare?
3. Is there a capability gap or surplus worth surfacing to leadership?
4. Is the peer's public posture different from their actual (per analyst commentary) — important for not over-indexing on marketing.

## Composes with

Standard Phase-1 foundation. Cross-feeds:
- `stakeholder-update-writer` — exec-tier "what are peers doing"
- `decision-memo-writer` (planned) — when peer activity informs a bank decision
- `vendor-security-eval` — when a peer's vendor adoption is the signal worth investigating
- [`executive-summary-writer`](../executive-summary-writer/SKILL.md) — **only when the user explicitly asks for an exec summary** (never auto-invoked after vault write). Takes the just-written research note's path and produces a 1-page summary tuned to a named audience (CISO, VP Eng, etc.).
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 30 done-criteria)

SKILL.md describes the source taxonomy + framing per finding. Live exercise deferred to first concrete peer-research invocation (when leadership asks a specific question about a specific peer).
