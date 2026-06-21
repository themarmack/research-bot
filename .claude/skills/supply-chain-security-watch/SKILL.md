---
name: supply-chain-security-watch
description: On-demand Category 1 researcher for software supply-chain security — SBOM standards (CycloneDX, SPDX), SLSA framework, Sigstore, in-toto, OpenSSF Scorecard, npm / PyPI / Maven malware trends, and major supply-chain incidents. Output at vault/research/supply-chain/YYYY-MM-DD-{slug}.md. Composes with sbom-reviewer (control side), daily-cve-digest (active matching side), and actions-workflow-hardener (workflow side). The Mini Shai-Hulud research at [[2026-06-20-actions-hardening-post-shai-hulud]] is the kind of output this skill produces on demand.
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

## Obsidian-first workflow

Same Phase-1 pattern.

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
