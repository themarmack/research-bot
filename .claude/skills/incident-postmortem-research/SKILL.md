---
name: incident-postmortem-research
description: On-demand Category 1 researcher for publicly-reported dev-tooling / supply-chain / AI-system incidents relevant to a current bank decision. Pulls the public postmortem (vendor disclosure, CISA advisory, post-incident analyst commentary, peer-bank disclosure if applicable), distills the technique + the missing control + the lesson, and maps to the org's current posture. Output at vault/research/sdlc-best-practice/YYYY-MM-DD-incident-{slug}.md. The Mini Shai-Hulud research at [[2026-06-20-actions-hardening-post-shai-hulud]] is an existing instance of this skill's output.
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
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 31 done-criteria)

The Mini Shai-Hulud research at [[2026-06-20-actions-hardening-post-shai-hulud]] is an existing instance of this skill's output. The 5-dimension framing is implicit in that note. No new live exercise required for step 31's acceptance.
