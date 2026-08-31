---
name: peer-bank-tech-intel
description: Collect what other major banks publicly share about their developer platforms, AI coding adoption, platform engineering, and SDLC modernization — engineering blogs (JPMorgan, Goldman Sachs, Morgan Stanley, Capital One, BofA, Wells Fargo, Citi, HSBC, Deutsche Bank, Barclays), conference talks (FS-ISAC, QCon Financial Services tracks), public RFCs / open-source projects, and named-analyst commentary. Output at vault/research/peer-bank/YYYY-MM-DD-{slug}.md. Composes with stakeholder-update-writer (exec asks "what are peers doing?") and decision-memo-writer. Use when the user asks what peer banks are publicly doing or saying about developer platforms, AI coding, or SDLC modernization — producing a fresh, cited research note from public sources only — not for evaluating a specific vendor's security posture (vendor-security-eval) or comparing AI coding tools (ai-coding-tools-compare).
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

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the peer's name and the capability's key terms across `vault/research/peer-bank/**`, relevant `vault/facts/**` entities (per-bank entities where they exist), `vault/insights/**` (conference-talk notes often carry peer-bank signals), and recent `vault/digests/**` (last 90 days).
   - Backlink check on the peer-bank entity (e.g. `[[jpmorgan]]`, `[[capital-one]]`) and the capability's entities.
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on the source taxonomy below — public sources only; never source from non-public material.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - A bank's own engineering blog is tier-1 for what THEY claim to do, but marketing-adjacent — any claim about outcomes or scale, and all analyst characterizations of a peer's actual posture, get the full 3-vote treatment.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/peer-bank/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic: peer-bank`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings framed per the 4 questions below (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/peer-bank-tech-intel/`:
   - Any verified fact-typed claim (e.g. "peer X publicly adopted vendor Y in {year}") → `_inbox/peer-bank-tech-intel/{timestamp}-{slug}.md` with `suggested_surface: facts` and a `suggested_path` under the matching `facts/` entity.
   - `memory-curator` decides on its next sweep.

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
- `decision-memo-writer` — when peer activity informs a bank decision
- `vendor-security-eval` — when a peer's vendor adoption is the signal worth investigating
- [`executive-summary-writer`](../executive-summary-writer/SKILL.md) — **only when the user explicitly asks for an exec summary** (never auto-invoked after vault write). Takes the just-written research note's path and produces a 1-page summary tuned to a named audience (CISO, VP Eng, etc.).
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 30 done-criteria)

SKILL.md describes the source taxonomy + framing per finding. Live exercise deferred to first concrete peer-research invocation (when leadership asks a specific question about a specific peer).
