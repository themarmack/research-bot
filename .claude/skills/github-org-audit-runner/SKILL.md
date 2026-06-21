---
name: github-org-audit-runner
description: Audit a GitHub organization's admin-surface settings — SAML / SCIM, EMU posture, base permissions, secret scanning + push-protection org defaults, allowed Actions list, runner groups, repository creation policies, IP allow-list — against the org's baseline. Uses `gh api` for live inspection where authenticated; falls back to a structured manual-checklist a human admin can walk through in the UI. Produces a posture report with `current_state` vs `expected_state` per item, severity, and remediation. Use during quarterly admin reviews, before audit conversations, or when troubleshooting a "why can't users do X" complaint that might be an org-wide policy.
---

# github-org-audit-runner

A Category 3 ops tool. The org's admin settings are a control surface auditors and security architecture care about. This skill makes the audit reproducible: same checks every time, same baseline, structured output.

## When to use

- Quarterly admin review (the cadence you'd use for `ghas-config-reviewer` but at org level).
- Before audit conversations needing documented org posture.
- Troubleshooting an org-wide-policy-induced issue (a team complaining their Action isn't allowed, a user complaining they can't push to a public fork).
- After a major GitHub product change that affects admin settings (model selection, AI policy, residency).

## When NOT to use

- Repo-level GHAS configuration → `ghas-config-reviewer`.
- Workflow security → `actions-workflow-hardener`.
- Specific user / membership questions → `enterprise-audit-log-investigator`.
- Copilot-specific policy → `copilot-faq-answerer` for the question, this skill for the org settings backing it.

## Baseline (the org's expected state)

Per category. Severities apply if the current state diverges.

### Identity & access

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| SAML SSO enforced | yes | CRITICAL |
| SCIM provisioning enabled | yes | HIGH |
| EMU (Enterprise Managed Users) posture | enabled for in-scope org(s) | HIGH |
| Two-factor required for non-SAML members | yes | CRITICAL |
| Outside collaborators allowed | no (or org-policy-approved exception list) | HIGH |

### Repository defaults

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Default branch protection on org-template repos | yes | HIGH |
| Base member permission | `read` (escalate per-repo) | HIGH |
| Repository creation by members | restricted to approved teams | MEDIUM |
| Repo deletion / transfer | admin-only | HIGH |
| Public repo creation | requires admin approval | HIGH |

### Security & code scanning

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Secret scanning org default | enabled | CRITICAL |
| Push protection org default | enabled | CRITICAL |
| Code scanning default-setup for new repos | enabled | HIGH |
| Dependabot alerts org default | enabled | HIGH |
| Dependabot security updates org default | enabled | HIGH |

### Actions

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Actions enabled for org | yes (where Actions is the standard CI surface) | INFO |
| Allowed Actions list | restricted (allow-list, not allow-all) | HIGH |
| GITHUB_TOKEN default permission | `read` | HIGH |
| Self-hosted runners | grouped + ephemeral | HIGH |
| Runner group scoping | scoped to specific orgs / repos | HIGH |

### Copilot

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Copilot policy assignment | per-team (not org-wide blanket) | INFO |
| Public code filter | on | CRITICAL |
| Content exclusions | per [[ip-indemnity]] + per-team additions | HIGH |
| Data residency | US (per [[data-residency-regions]]) | HIGH |
| Approved model list | matches MRM/TPRM record | HIGH |

### Audit & monitoring

| Setting | Expected | Severity if missing |
|---------|----------|---------------------|
| Audit log streaming to SIEM | enabled (S3 + KMS path per [[audit-log-export-format]]) | HIGH |
| IP allow-list | enabled for admin access (if org policy requires) | HIGH |

## Workflow

1. **Authenticate** — confirm `gh auth status` shows access to the target org with admin scope.
2. **Inspect via `gh api`** for each baseline category:
   - `gh api orgs/{org}` — basic settings
   - `gh api orgs/{org}/credential-authorizations` — SAML enforcement
   - `gh api orgs/{org}/scim/v2/Users` — SCIM presence
   - `gh api orgs/{org}/actions/permissions` — Actions allow-list
   - `gh api orgs/{org}/actions/runner-groups` — runner groups
   - `gh api orgs/{org}/copilot/billing` — Copilot policy
   - `gh api orgs/{org}/security-and-analysis` — secret/code scanning defaults
   - `gh api enterprises/{enterprise}/audit-log` — streaming endpoint
3. **Compare** each setting against the baseline.
4. **Produce findings** — structured list per category.
5. **If auth fails**: emit the manual checklist (below) for a human admin to walk through in the UI.

## Manual-checklist fallback

When `gh api` isn't authenticated, output a printable checklist the user can walk through in https://github.com/organizations/{org}/settings. Each item has the UI navigation path + expected state.

Example items:
- `[ ] Settings → Authentication security → SAML SSO → enforced for org members`
- `[ ] Settings → Code security and analysis → Secret scanning → enabled by default for new repos`
- `[ ] Settings → Actions → General → Actions permissions → "Allow enterprise, and select non-enterprise, actions and reusable workflows"`

## Output shape

```json
{
  "target_org": "bank-org-name",
  "audit_run_at": "2026-06-20T16:00:00Z",
  "auth_status": "live | manual_fallback",
  "findings": [
    {
      "category": "identity-access",
      "check": "SAML SSO enforced",
      "current_state": "enforced",
      "expected_state": "enforced",
      "verdict": "pass",
      "severity": "info"
    },
    {
      "category": "actions",
      "check": "Allowed Actions list",
      "current_state": "allow-all",
      "expected_state": "restricted allow-list",
      "verdict": "fail",
      "severity": "high",
      "remediation": "Settings → Actions → General → Allow specific actions. Add the org's approved-Actions list.",
      "reference": "vault/research/github/2026-06-20-actions-hardening-post-shai-hulud.md"
    }
  ],
  "summary": {"critical":0,"high":2,"medium":1,"low":0,"info":15,"total":18}
}
```

## Composes with

- `gh` CLI (user-authenticated).
- `ghas-config-reviewer` — sister skill at the repo level.
- `vault-querier` — facts for Copilot-specific baseline items.

## Acceptance test (for step 17 done-criteria)

Produce one audit run output (live or manual fallback). Confirm:
- All 6 baseline categories present in findings.
- Each finding has `current_state`, `expected_state`, `verdict`, `severity`.
- Summary block has the right counts.
- Failed items include a `remediation` + `reference` (vault note or GitHub Docs URL).
