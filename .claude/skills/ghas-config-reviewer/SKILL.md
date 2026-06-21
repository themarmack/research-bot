---
name: ghas-config-reviewer
description: Audit a GitHub repo or org's GitHub Advanced Security configuration against the org's baseline. Checks code scanning enablement, secret scanning + push protection, Dependabot alerts + version updates, dependency review, branch protection requiring GHAS checks, and CODEOWNERS hygiene. Uses `gh api` for live inspection of a target repo or org; falls back to documented baseline check items the user can run manually. Produces a structured finding list with severity, current vs expected state, and remediation steps. Use during repo onboarding, periodic GHAS audits, or before stakeholder reviews of GHAS posture.
---

# ghas-config-reviewer

A Category 3 ops tool. The user runs this against a repo (or org) and gets a structured posture report: what's configured, what's missing relative to the baseline, what's misconfigured.

## When to use

- New-repo onboarding review.
- Periodic sweep across the org's important repos (high-blast-radius, regulated-data-handling, etc.).
- Before stakeholder reviews of GHAS posture (legal, audit, security architecture).
- Validating that an exception expired and the baseline is now enforced.

## When NOT to use

- Workflow-level review → `actions-workflow-hardener`.
- Repository-level governance beyond GHAS (CODEOWNERS specifics, ruleset patterns) → `repo-golden-path-scorer` (planned).
- Investigating a specific CodeQL alert → that's CodeQL triage, not configuration review.

## Baseline (the org's expected state)

This is the documented expected state for a "fully GHAS-onboarded" repo in the org. Deviations get flagged.

### Code scanning

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Code scanning enabled | yes | CRITICAL |
| Setup mode | default OR advanced (org policy permits both) | INFO |
| Default queries plus security-extended | yes | HIGH |
| Custom CodeQL pack from the org | yes (for in-scope languages) | MEDIUM |
| Code scanning required on PR before merge | yes | HIGH |
| Workflow files scanned (advanced setup) | yes | MEDIUM |

### Secret scanning

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Secret scanning enabled | yes | CRITICAL |
| Push protection enabled | yes | CRITICAL |
| Custom patterns (org's internal secret formats) | yes | HIGH |
| Push-protection bypass requires justification | yes (audit-logged) | HIGH |

### Dependabot

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Dependabot alerts enabled | yes | CRITICAL |
| Dependabot security updates enabled | yes | HIGH |
| Dependabot version updates enabled (per `dependabot.yml`) | yes (with grouped updates) | MEDIUM |
| Auto-triage rules (auto-dismiss low/dev-dep) | optional but recommended | LOW |

### Dependency review

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Dependency review required on PR | yes | HIGH |
| License denylist enforced | yes (per org's allowed-licenses list) | MEDIUM |

### Branch protection

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Required status checks include code scanning | yes | HIGH |
| Required status checks include dependency review | yes | HIGH |
| Require PRs (no direct push to default) | yes | CRITICAL |
| Require CODEOWNERS review | yes | HIGH |
| Restrict who can dismiss reviews | yes (CODEOWNERS only) | MEDIUM |

### Actions allowed list

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Actions restricted to org allow-list | yes | HIGH |
| Marketplace actions require explicit allow | yes | HIGH |

## Workflow

1. **Identify target** — the user provides a repo (`owner/repo`) or org name.
2. **Inspect via `gh api`**:
   - `gh api repos/{owner}/{repo}` for repo settings.
   - `gh api repos/{owner}/{repo}/code-scanning/default-setup` for code scanning state.
   - `gh api repos/{owner}/{repo}/branches/{default}/protection` for branch protection.
   - `gh api repos/{owner}/{repo}/secret-scanning/alerts` for secret scanning enablement (presence of the endpoint signals enabled).
   - `gh api repos/{owner}/{repo}/vulnerability-alerts` for Dependabot alerts.
   - `gh api repos/{owner}/{repo}/contents/.github/dependabot.yml` for version update config.
   - `gh api orgs/{org}/actions/permissions` for org-level Actions allow-list (when org-scoped).
3. **Compare** each setting against the baseline above.
4. **Produce findings** — structured list as below.

If `gh api` access fails (no auth, no permission), **stop and report**: emit a manual checklist the user can run.

## Output shape

```json
{
  "target": "owner/repo",
  "findings": [
    {
      "check_id": "GHAS-SEC-001",
      "category": "secret-scanning",
      "severity": "critical",
      "current_state": "disabled",
      "expected_state": "enabled with push protection",
      "remediation": "Enable secret scanning via Settings → Code security and analysis. Then enable push protection. Both are no-cost for GHAS-licensed repos.",
      "reference": "GitHub Docs — About secret scanning"
    }
  ],
  "summary": {"critical": 0, "high": 2, "medium": 3, "low": 0, "info": 5, "total": 10}
}
```

Group findings by category (code-scanning, secret-scanning, dependabot, dependency-review, branch-protection, actions-allowlist).

## Composes with

- The user's `gh` CLI (already authenticated to the org).
- `vault-querier` — surface related research / prior audits.
- Related skills: `actions-workflow-hardener` (workflow-level), `codeql-onboarding-helper` (planned), `dependabot-config-helper` (planned).

## Acceptance test (for step 13 done-criteria)

Run against a target repo the user nominates. Expected:
- Successful `gh api` calls for all baseline endpoints, OR a manual-checklist fallback if auth fails.
- Findings list grouped by category with severity correctly assigned.
- Each finding has a remediation step that's concrete and actionable.

Live exercise deferred to first real invocation (requires `gh` CLI auth + a target repo).
