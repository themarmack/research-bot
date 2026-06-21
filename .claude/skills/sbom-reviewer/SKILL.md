---
name: sbom-reviewer
description: Parse a CycloneDX or SPDX SBOM and flag supply-chain concerns BEYOND what CVE matching catches — unsigned releases, abandoned packages (no commits in 12+ months), single-maintainer critical dependencies, known-malicious authors / typo-squat patterns, license conflicts, SBOM completeness (declared vs actual depth). Produces a structured finding list with severity and remediation. Composes with daily-cve-digest (which handles the CVE side) and license-compliance-checker (which handles the licensing side); this skill covers the structural risk surface.
---

# sbom-reviewer

The supply-chain risk dimension that **isn't** CVE matching. CVE flagging is well-served by `daily-cve-digest` + Dependabot; this skill covers structural concerns: who maintains the code, are releases signed, is the SBOM complete.

## When to use

- New SBOM published — review for structural concerns before adopting the artifact.
- Vendor SBOM provided — assess the vendor's supply chain.
- Annual portfolio audit of declared dependencies' supply-chain posture.
- After a publicized supply-chain incident — re-scan for the affected pattern.

## When NOT to use

- CVE matching → `daily-cve-digest`.
- License compliance → `license-compliance-checker`.
- Workflow security → `actions-workflow-hardener`.

## Input

- **CycloneDX JSON** (`bom.json`) or **SPDX** (`spdx.json` / `spdx.yaml`)
- Optionally: lockfile cross-reference (to verify SBOM matches actual dependencies)

## Checks

### 1. Signing + provenance

| Check | Severity |
|-------|----------|
| Component declares `pedigree` or `provenance` with signed attestation (SLSA / sigstore) | INFO when present, MEDIUM when absent for tier-1 deps |
| Component release tagged but no signature on the tag | HIGH for critical-library deps |
| Component publisher matches expected upstream identity | HIGH if mismatch |

### 2. Maintenance health

| Check | Severity |
|-------|----------|
| Last upstream commit > 12 months ago (abandoned) | HIGH |
| Last release > 24 months ago | MEDIUM |
| Single maintainer on a critical-library tier dep | HIGH (per [[daily-cve-digest]]'s `critical_libraries` config) |
| Maintainer departed publicly (e.g., maintainer announced retirement / hand-off pending) | MEDIUM |

### 3. Known-malicious / typo-squat

| Check | Severity |
|-------|----------|
| Package name matches a known typo-squat pattern (Levenshtein ≤ 2 from a popular package, but newer publisher) | CRITICAL |
| Maintainer email / account in known-bad publisher list (per OpenSSF / community advisories) | CRITICAL |
| Package publisher recently transferred (within 90d) for a critical-library dep | HIGH |

### 4. SBOM completeness

| Check | Severity |
|-------|----------|
| Declared dependency depth < actual lockfile depth | HIGH |
| Components missing version OR purl | MEDIUM |
| Hashes missing for components | MEDIUM |
| Components present in lockfile not in SBOM | HIGH |

### 5. License consistency

| Check | Severity |
|-------|----------|
| Component license declared in SBOM differs from upstream registry declaration | HIGH (potential mislabeling) |
| Component lacks any license declaration | MEDIUM |

## Workflow

1. **Parse the SBOM** (CycloneDX or SPDX).
2. **For each component**: run the 5 check categories.
3. **Cross-reference** against `daily-cve-digest/stack.yml` to identify which components are critical-library tier (severity boost).
4. **Produce findings**: per-component, per-check.
5. **Summary**: posture score (% of components passing), top concerns by severity.

## Output structure

```markdown
# SBOM Review — {SBOM filename or service}

## Summary
- Components in SBOM: {N}
- Findings: {M} ({critical/high/medium counts})
- Posture score: {%} of components pass all structural checks

## Top concerns
[per concern: component + reason + severity]

## Findings by category
[per category, listed]

## Cross-reference: critical libraries
- {Critical-library deps present + structural posture summary}

## Sources
{linked vault notes, stack.yml}
```

Lands at `vault/research/supply-chain/YYYY-MM-DD-sbom-{service-slug}.md`.

## Composes with

- [`daily-cve-digest`](../daily-cve-digest/SKILL.md) — `stack.yml` is the critical-library reference.
- [`license-compliance-checker`](../license-compliance-checker/SKILL.md) — license dimension.
- [[2026-06-20-actions-hardening-post-shai-hulud]] — supply-chain context.

## Acceptance test (for step 26 done-criteria)

5 check categories documented; each with named checks + severity. Live exercise against a real SBOM deferred to first invocation.
