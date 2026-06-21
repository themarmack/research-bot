---
name: license-compliance-checker
description: Scan a dependency tree (Maven / npm / pip / Go / Cargo / NuGet) and flag licenses against the org's allow / review / deny list. Allowed: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense. Review-required: LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0, CDDL-1.0 (case-by-case). Denied: GPL-2.0, GPL-3.0, AGPL-3.0, SSPL, BUSL, CC-BY-NC, proprietary, custom. Surfaces transitive license risks (a permissive package depending on a denied one). Produces a structured finding list with severity, dep tree path, suggested remediation. Use during dependency-review PR phase, before going to production with a new dependency, or as a portfolio audit step.
---

# license-compliance-checker

A Category 4 ops tool. License compliance is the surface where AppSec, legal, and procurement collide — and where dependency adoption stalls without a clear allow/review/deny posture. This skill makes the org's posture explicit and the scan reproducible.

## When to use

- Dependency review PR phase (a new dependency added — does its license stand?).
- Before going to production with a service that uses a new dependency.
- Portfolio audit: scan N repos' dependency trees for risky licenses.
- After a license change at the upstream level (e.g., Elastic licensing change, Hashicorp BUSL move) — re-scan for impact.

## When NOT to use

- Code-level review → CodeQL.
- IP indemnity question for AI tool output → [`copilot-faq-answerer`](../copilot-faq-answerer/SKILL.md) `ip-indemnity` entry.
- License authorship review (the org's own code) → that's a different process.

## Org's license posture (the allow / review / deny list)

### Allowed (no further review)

- **MIT** — permissive, no copyleft, attribution required
- **Apache-2.0** — permissive, patent grant included
- **BSD-2-Clause** (Simplified BSD)
- **BSD-3-Clause** (Modified BSD)
- **ISC** — equivalent to MIT
- **Unlicense** — public-domain dedication
- **0BSD** — zero-clause BSD
- **CC0-1.0** — public domain (note: NOT same as CC-BY-NC)
- **Zlib** — permissive
- **Python-2.0**, **PSF-2.0** — Python software foundation

### Review-required (case-by-case)

These need legal review before adoption:

- **LGPL-2.1 / LGPL-3.0** — weak copyleft; OK for dynamic linking, problematic for static/embedded
- **MPL-2.0** — file-level copyleft; OK if used unmodified, careful if forked
- **EPL-2.0** — weak copyleft, file-based
- **CDDL-1.0** — weak copyleft, file-based
- **CPL-1.0** — older variant of EPL
- **Artistic-2.0** — Perl Foundation; review needed for embedded contexts

### Denied (do not adopt without an exception)

- **GPL-2.0 / GPL-3.0** — strong copyleft; risk to proprietary code combined with GPL dependency
- **AGPL-3.0** — network copyleft; particularly risky for SaaS-style services
- **SSPL-1.0** (Server Side Public License) — non-OSI-approved; explicit obligations on org's service
- **BUSL-1.1** (Business Source License) — time-bombed source-available; not free; obligation post-conversion
- **CC-BY-NC** (non-commercial) — incompatible with org's commercial use
- **CC-BY-ND** (no derivatives) — incompatible with normal usage
- **Proprietary / "All rights reserved"** — requires explicit commercial agreement
- **Custom licenses** — explicit review required regardless of permissiveness

### Transitive concerns

A package with an Allowed license depending on a Review-required or Denied package: the transitive license obligation flows through. The skill traces the full tree and surfaces transitive risks separately from direct ones.

## Workflow

1. **Identify the dep tree**: parse `pom.xml` + lockfile / `package-lock.json` / `poetry.lock` / `go.sum` / etc.
2. **Resolve licenses**: each package's declared license (per its registry metadata).
3. **Categorize**: allowed / review / deny.
4. **Trace transitives**: for any Review or Deny finding, identify the path from a direct dependency to it.
5. **Produce findings**: structured list per package + license + verdict + remediation.

## Output structure

```markdown
# License Compliance — {repo / target}

## Summary
- Direct dependencies: {N}
- Transitive: {M}
- Allowed: {A} | Review-required: {R} | Denied: {D}

## Denied direct dependencies (must remediate)
| Package | Version | License | Remediation |
|---------|---------|---------|-------------|

## Denied transitive dependencies
| Package | Version | License | Via direct dep | Remediation |
|---------|---------|---------|----------------|-------------|

## Review-required (legal review queue)
[same shape]

## Notable allowed (informational)
[high-profile dependencies for audit visibility]
```

Lands at `vault/research/sdlc-best-practice/YYYY-MM-DD-license-compliance-{repo-slug}.md`.

## Composes with

- `dependabot-config-helper` — Dependabot itself doesn't have a license-deny step; this skill fills the gap.
- `sbom-reviewer` (step 26) — natural pair; SBOMs include license metadata.
- `vault-querier` — load prior license-compliance findings to track repo-level trends.

## Acceptance test (for step 25 done-criteria)

The allow/review/deny lists shipped per category. SKILL.md describes the workflow + transitive-tracing approach + output shape. Live exercise against a real repo deferred until first invocation.
