---
name: supply-chain-security-watch
description: On-demand Category 1 researcher for software supply-chain security — SBOM standards (CycloneDX, SPDX), SLSA framework, Sigstore, in-toto, OpenSSF Scorecard, npm / PyPI / Maven malware trends, and major supply-chain incidents. Output at vault/research/supply-chain/YYYY-MM-DD-{slug}.md. Composes with sbom-reviewer (control side), daily-cve-digest (active matching side), and actions-workflow-hardener (workflow side). The Mini Shai-Hulud research at [[2026-06-20-actions-hardening-post-shai-hulud]] is the kind of output this skill produces on demand. Use when the user asks to research a supply-chain security standard, framework, ecosystem trend, or landscape question on demand — producing a fresh, cited research note — not for the scheduled stack-matched CVE roundup (daily-cve-digest), auditing a specific SBOM (sbom-reviewer), or dissecting one specific incident (incident-postmortem-research).
---

# supply-chain-security-watch

The "what's happening in supply-chain security right now" skill. Distinct from `daily-cve-digest` (which surfaces specific CVEs against the org's stack) and `sbom-reviewer` (which audits a specific SBOM) — this is the policy/landscape lens that informs the others.

## When to use

- New supply-chain incident in the news (post-mortem worth reading).
- A standard / spec evolves (SLSA v1 → v2, CycloneDX schema bump).
- Vendor's SBOM completeness question — need to know what "good" looks like in current state.
- Annual supply-chain posture review.

## Topic taxonomy

- `slsa` — Supply chain Levels for Software Artifacts
- `sbom-standards` — CycloneDX, SPDX
- `sigstore` — signing infrastructure
- `in-toto` — attestation framework
- `openssf-scorecard` — project health signals
- `supply-chain-incidents` — specific attacks (Shai-Hulud-class, npm/PyPI takeovers)
- `ecosystem-trends` — npm / PyPI / Maven / etc. specific patterns

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the question's key terms across `vault/research/supply-chain/**`, `vault/research/github/**` (Actions-hardening notes live there), relevant `vault/facts/**` entities (e.g. `slsa`, `sigstore`), and recent `vault/digests/**` (last 90 days — `daily-cve-digest` and `weekly-intelligence-digest` carry supply-chain items).
   - Backlink check on the topic's entities (e.g. `[[slsa]]`, `[[sbom]]`, `[[sigstore]]`).
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: slsa.dev, CycloneDX / SPDX spec sites, sigstore.dev, in-toto.io, OpenSSF blog + Scorecard docs, CISA advisories, ecosystem registries' official security posts (npm, PyPI, Maven Central).
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - Spec text and official advisories are tier-1 (no verification); incident attribution and trend claims from analyst commentary get the full 3-vote treatment.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/supply-chain/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic` from the taxonomy above, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/supply-chain-security-watch/`:
   - Any verified fact-typed claim → `_inbox/supply-chain-security-watch/{timestamp}-{slug}.md` with `suggested_surface: facts` and a `suggested_path` under the matching `facts/` entity.
   - `memory-curator` decides on its next sweep.

## Compliance-relevant framing per finding

For each finding:
1. Does this change what the org's `sbom-reviewer` looks for?
2. Does this require a new entry in `daily-cve-digest/stack.yml`?
3. Does this map to a new `actions-workflow-hardener` rule?
4. Does this require communication to stakeholders?

## Composes with

- `sbom-reviewer` — control-side.
- `daily-cve-digest` — matching-side.
- `actions-workflow-hardener` — workflow-side.
- `openssf-blog` source in `source-registry`.

## Acceptance test (for step 29 done-criteria)

The Mini Shai-Hulud research at [[2026-06-20-actions-hardening-post-shai-hulud]] is an existing instance of what this skill produces. No new live exercise required for this step's acceptance.
