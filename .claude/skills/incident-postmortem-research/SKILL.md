---
name: incident-postmortem-research
description: On-demand Category 1 researcher for publicly-reported dev-tooling / supply-chain / AI-system incidents relevant to a current bank decision. Pulls the public postmortem (vendor disclosure, CISA advisory, post-incident analyst commentary, peer-bank disclosure if applicable), distills the technique + the missing control + the lesson, and maps to the org's current posture. Output at vault/research/incident/YYYY-MM-DD-{slug}.md. The Mini Shai-Hulud research at [[2026-06-20-actions-hardening-post-shai-hulud]] is an existing instance of this skill's output. Use when the user asks to research, distill, or learn from a specific publicly-reported incident — producing a fresh, cited research note mapped to org posture — not for internal incidents (org incident-response process), the recurring news sweep (weekly-intelligence-digest), or landscape-level supply-chain questions (supply-chain-security-watch).
---

# incident-postmortem-research

The "learn from somebody else's bad day" skill. Most incidents in dev tooling, supply chain, and AI systems get publicly analyzed — the org can absorb the lesson without paying for the incident.

## When to use

- New publicly-reported incident affecting dev tooling, supply chain, or AI systems.
- Decision under consideration: would adopting X expose the org to the same pattern that hit Y?
- After a near-miss internally: similar published incidents to learn from?
- Annual portfolio retro: what classes of incident affected peers this year?

## When NOT to use

- Internal incidents → handled via the org's incident-response process, not this skill.
- Current event reporting → `weekly-intelligence-digest` covers the recurring case.
- Generic supply-chain research → `supply-chain-security-watch` for landscape; this skill for specific incidents.

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the incident's name and key terms across `vault/research/incident/**`, `vault/research/sdlc-best-practice/**` and `vault/research/supply-chain/**` (older incident notes live there), relevant `vault/facts/**` entities, and recent `vault/digests/**` (last 90 days — `daily-cve-digest` and `weekly-intelligence-digest` often carry first reports of the incident).
   - Backlink check on the incident's entities (affected vendor, ecosystem, technique).
2. **Triage findings**:
   - If the vault already covers this incident fully → return the existing analysis with source citations (vault path + original source URLs). No new write.
   - If partial (e.g. first report captured but no postmortem analysis) → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on the source taxonomy below, preferring the vendor's official postmortem and CISA advisories over commentary.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - The vendor's own disclosure and CISA advisories are tier-1 (no verification); attribution claims, impact estimates, and analyst reconstructions of the attack chain get the full 3-vote treatment.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/incident/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic: incident`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + the 5-dimension framing below + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/incident-postmortem-research/`:
   - Any verified fact-typed claim (e.g. a confirmed missing-control pattern worth adding to the threat catalog) → `_inbox/incident-postmortem-research/{timestamp}-{slug}.md` with `suggested_surface: facts` and a `suggested_path` under the matching `facts/` entity.
   - `memory-curator` decides on its next sweep.

## Source taxonomy

- **Vendor incident disclosures** — official post-mortems and security advisories.
- **CISA advisories** — KEV (Known Exploited Vulnerabilities) catalog + CISA ICS / CSAS advisories.
- **OpenSSF / community advisories** — supply-chain-specific incident analyses.
- **Analyst commentary** — named-analyst incident analyses (Krebs, Wired, The Hacker News post-mortems).
- **Peer-bank disclosures** — when a peer bank publicly discloses (uncommon but valuable when present).
- **Academic / research conference postmortems** — USENIX, Black Hat, DEF CON.

## Output framing per incident

Each incident gets analyzed on 5 dimensions:

1. **What happened** — the technical chain.
2. **Missing control** — what specific control would have prevented or detected.
3. **Bank posture** — does the org's current posture address the missing control?
4. **Lesson** — generalized takeaway.
5. **Action** — what (if anything) does this trigger for the org?

## Composes with

- `supply-chain-security-watch` — broader landscape context.
- `threat-model-helper` — when an incident pattern should be added to the threat catalog.
- `secure-design-reviewer` — when an incident reveals a control category gap.
- [`executive-summary-writer`](../executive-summary-writer/SKILL.md) — **only when the user explicitly asks for an exec summary** (never auto-invoked after vault write). Takes the just-written research note's path and produces a 1-page summary tuned to a named audience (CISO, VP Eng, etc.).
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 31 done-criteria)

The Mini Shai-Hulud research at [[2026-06-20-actions-hardening-post-shai-hulud]] is an existing instance of this skill's output. The 5-dimension framing is implicit in that note. No new live exercise required for step 31's acceptance.
