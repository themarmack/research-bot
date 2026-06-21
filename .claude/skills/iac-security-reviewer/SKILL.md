---
name: iac-security-reviewer
description: Review Terraform / Bicep / CloudFormation files for security misconfigurations against CIS benchmarks + org guardrails. Favors existing checkov/tfsec/kics rule semantics (the user already knows them). Bank-guardrail additions cover: data-residency-pinning (resources must declare region), encryption-at-rest mandatory (no defaults), tagging discipline (data-classification + cost-center tags required), public-network exposure (no `0.0.0.0/0` ingress to anything except documented edge resources). Produces a structured finding list with rule_id, severity, line, snippet, remediation. Use whenever reviewing new IaC before merge, refactoring legacy IaC, or auditing IaC across a portfolio.
---

# iac-security-reviewer

A Category 4 ops tool. Bank IaC sits at the intersection of (a) standard CIS / cloud-provider security recommendations, (b) the org's own guardrails (region pinning, tagging, encryption mandatory), and (c) regulatory expectations (FFIEC IT Handbook on cloud risk, OCC bulletins on third-party cloud). This skill makes the review reproducible.

## When to use

- New Terraform / Bicep / CFN file before merge.
- Refactoring legacy IaC that pre-dates current guardrails.
- Portfolio audit of multiple repos' IaC.
- After a cloud-provider security bulletin: targeted re-check for the affected resource pattern.

## When NOT to use

- Application code review → CodeQL or `secure-design-reviewer`.
- IaC runtime behavior (the actual deployed state) → cloud-provider security center.
- Cost optimization → not the security lens.

## Checks (each maps to a `rule_id`)

### Standard CIS / cloud-provider (~50 rules — favoring checkov / tfsec / kics semantics)

The user already knows checkov / tfsec rule IDs (e.g., `CKV_AWS_20` for S3 ACL, `AWS001` for S3 bucket logging). This skill *references* those rule IDs rather than re-implementing them. If the user has checkov / tfsec / kics installed locally, prefer running those first and consuming their output.

### Bank-specific guardrails

| `rule_id` | Severity | Check |
|-----------|----------|-------|
| `ORG-IAC-001` | CRITICAL | Resource must declare explicit region (no inheriting from provider default — region must be in-config for residency audit) |
| `ORG-IAC-002` | CRITICAL | Encryption-at-rest required for any data store (S3 / RDS / DynamoDB / EBS) — no relying on cloud-provider default |
| `ORG-IAC-003` | HIGH | Required tags: `data-classification`, `cost-center`, `owner-team`, `compliance-scope` |
| `ORG-IAC-004` | CRITICAL | Public-network exposure: no `0.0.0.0/0` ingress except for documented edge resources (which need a `org:edge-exposure-approved` tag with a decision-note reference) |
| `ORG-IAC-005` | HIGH | KMS keys must be customer-managed (CMK), not AWS-managed |
| `ORG-IAC-006` | HIGH | IAM policies must not use `*` actions on `*` resources |
| `ORG-IAC-007` | MEDIUM | S3 buckets must have versioning enabled |
| `ORG-IAC-008` | MEDIUM | RDS instances must have automated backups with retention ≥ 7 days |
| `ORG-IAC-009` | HIGH | Lambda / Azure Functions / Cloud Functions must declare `runtime` explicitly (not `latest`) for reproducibility + EOL tracking |
| `ORG-IAC-010` | MEDIUM | Logs to org SIEM endpoint via CloudWatch / Log Analytics / equivalent |

## Output shape

```json
{
  "file": "{path}",
  "findings": [
    {
      "rule_id": "ORG-IAC-004",
      "severity": "critical",
      "line": 17,
      "snippet": "cidr_blocks = [\"0.0.0.0/0\"]",
      "message": "Public-network ingress to a non-edge resource",
      "remediation": "Restrict cidr_blocks to org's VPC range or known partner CIDR. If this is intentionally edge-exposed, add tag org:edge-exposure-approved = true with a vault decision-note reference."
    }
  ],
  "summary": {"critical":1, "high":2, "medium":1, "low":0, "total":4}
}
```

## Composes with

- Local `checkov` / `tfsec` / `kics` if available — consume their output and add org-specific rules.
- [`secure-design-reviewer`](../secure-design-reviewer/SKILL.md) — for design-doc-level concerns the IaC reviewer doesn't catch.

## Acceptance test (for step 25 done-criteria)

Run against `tests/bad-terraform.tf` (in this skill folder). Expected: ≥5 findings spanning critical + high + medium severities; org-specific guardrails trigger on the deliberate violations.
