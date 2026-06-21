---
name: dependabot-config-helper
description: Generate or review a `.github/dependabot.yml` for a target repo or service, calibrated to org policy (regulated-environment defaults from `dependabot-strategy` research) and the repo's actual stack. Handles grouped updates (security + version separately), schedule cadence per ecosystem, private-registry integration, auto-merge gating, reviewer routing, and the open-pull-requests-limit per ecosystem. Use whenever onboarding a repo to Dependabot, refactoring an existing config that's drowning the team in PRs, or auditing a sample of org repos for config consistency.
---

# dependabot-config-helper

A Category 3 ops tool. The user runs this against a target repo (or a paste of an existing `dependabot.yml`) and gets either a from-scratch config or a reviewed-and-recommended-changes diff. Defaults come from `dependabot-strategy` research — config follows policy, not the other way around.

## When to use

- Onboarding a new repo to Dependabot — generate a starting `dependabot.yml`.
- Existing repo's Dependabot has gone off-rails (PR storm, ignored alerts, no security update path) — refactor.
- Org-wide audit: are repos' configs consistent with the policy?
- Adding a new ecosystem (npm + adding Docker, or Python + adding Terraform).

## When NOT to use

- Strategic / policy questions → `dependabot-strategy`.
- Individual alert triage / suppression → out of scope for v1.
- Multi-repo sweeps to rewrite configs at scale — possible but the user should review the generated configs individually for now.

## Required inputs

- **Target stack**: list of ecosystems present in the repo (npm, Maven, pip, Docker, Terraform, Go, etc.).
- **Regulatory exposure**: same lens as `copilot-rollout-playbook` — PCI-DSS, SOX, GDPR. Affects schedule + auto-merge defaults.
- **Team size + bandwidth**: affects `open-pull-requests-limit`. Small team → smaller limit + monthly cadence. Large team → larger limit + weekly cadence.
- **Private registries used** (if any): for `registries:` block.
- **Reviewer team handle**: for the `reviewers:` field.

## Bank-specific defaults (loaded from `dependabot-strategy` research)

These defaults come from the strategy research; they're not generic GitHub guidance.

- **Schedule cadence** per ecosystem:
  - npm / pip / Go / Maven / Gradle: **weekly** (active velocity, weekly batch tolerable)
  - Docker / Terraform: **monthly** (base-image / module updates have higher blast radius)
  - GitHub Actions: **weekly** (per the Mini Shai-Hulud lens — Action versions matter)
- **Grouped updates**:
  - Always group `applies-to: security-updates` separately from `applies-to: version-updates`
  - Within version updates: group `minor + patch` together; `major` updates always individual
- **`open-pull-requests-limit`**: default **5**; for teams smaller than 5 devs, set to **3**
- **Cooldown**: **3 days** on new releases for high-stakes ecosystems (npm, pip, Maven). Catches the worst supply-chain-attack windows.
- **Reviewers**: route security-updates to `@security-team`; version-updates to the repo's CODEOWNERS-implied team
- **Labels**: `security`, `dependency-update` for trackability
- **Target branch**: default branch UNLESS the repo has a gated `develop` branch
- **Commit message convention**: `chore(deps):` prefix for version, `fix(security):` for security updates

## Workflow

1. **If generating**:
   a. Take inputs.
   b. Apply org defaults per ecosystem.
   c. Compose the YAML.
   d. Output the file content + a one-paragraph rationale per ecosystem.
2. **If reviewing**:
   a. Read the existing config.
   b. Diff against org defaults.
   c. Output the findings list (each with current / expected / severity / remediation).
   d. Produce a recommended-changes diff.

## Output

A complete `.github/dependabot.yml` ready to commit, with header comments explaining the policy basis. Plus a sibling note at `vault/research/github/YYYY-MM-DD-dependabot-config-{repo-slug}.md` documenting the generation reasoning for audit.

## Composes with

- [`dependabot-strategy`](../dependabot-strategy/SKILL.md) — defaults source.
- `ghas-config-reviewer` — the Dependabot section of the GHAS baseline is informed by this skill's output.
- `repo-golden-path-scorer` (planned) — golden-path scoring includes presence + currency of `dependabot.yml`.

## Acceptance test (for step 18 done-criteria)

Generate a `dependabot.yml` for a hypothetical target (e.g., Payments Engineering: Java + npm + Docker, regulated-data exposure). Confirm:
- All declared ecosystems represented.
- Grouped updates split security vs version.
- Schedule cadence matches the per-ecosystem defaults.
- `open-pull-requests-limit` set.
- Reviewer routing present.
- Header comment documents the policy basis with a date.
