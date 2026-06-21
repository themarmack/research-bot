---
name: secure-coding-standard-checker
description: Check a code snippet against the org's secure-coding standards — patterns that go beyond what CodeQL flags by default. Covers: deprecated internal APIs, hard-coded business rules that should be config, regulatory pattern violations (PAN logging, customer-ID exposure in error responses), org-internal naming + structure conventions for security-sensitive components, the org's preferred crypto primitives + key lifetimes. Cites the relevant internal standard section per finding. Use during PR review for security-sensitive code, when triaging a CodeQL alert that needs higher-level context, or when refactoring a legacy module against current standards.
---

# secure-coding-standard-checker

The skill that catches what CodeQL misses — the org-specific layer on top of community queries. Most regulated orgs have a secure-coding standards document; this skill makes the checks reproducible.

## When to use

- PR review for code in security-sensitive paths (auth, crypto, customer-data handling).
- Triaging a CodeQL alert that needs the org-specific context (e.g., "is this a legitimate exception to our standard or a real violation?").
- Refactoring legacy code against the current standards.
- Pre-deployment check for security-sensitive modules.

## When NOT to use

- Generic code-quality review → CodeQL `security-and-quality` suite.
- Vulnerability-class scanning → CodeQL `security-extended` suite + `codeql-pattern-finder` for custom patterns.
- Workflow security → `actions-workflow-hardener`.

## Check categories

### 1. Deprecated internal APIs

| Pattern | Severity |
|---------|----------|
| `LegacyAuth.signWith(...)` — replaced by `org.auth.SignedToken` Q1 2026 | HIGH |
| `OldCryptoHelper.encrypt(...)` — pre-FIPS implementation, replaced by `org.crypto.FipsAesCbc` | CRITICAL |
| `LegacyDirectJdbc.rawExecute(...)` — bypasses org's data-access wrapper; should use `BankSecureJdbcWrapper` | HIGH |
| `com.org.legacy.*` namespace usage in new code | MEDIUM |

(This list is illustrative; the actual org's deprecated-API set is maintained as a separate config file the skill loads.)

### 2. Hard-coded business rules

| Pattern | Severity |
|---------|----------|
| Numeric thresholds (transaction limits, retry counts) hard-coded in production paths | HIGH |
| Account-type case statements hard-coded (should be table-driven) | MEDIUM |
| Regulatory thresholds (Reg E, Reg Z) embedded in code | CRITICAL — must come from config |

### 3. Regulatory pattern violations

| Pattern | Severity |
|---------|----------|
| PAN (16-digit card number) format in `log.*()` invocations | CRITICAL |
| Customer ID in `Exception.getMessage()` returned to caller | HIGH |
| SSN / Tax-ID in error responses or logs | CRITICAL |
| Card-CVV anywhere in persistence layer | CRITICAL |

### 4. Bank conventions for security-sensitive components

| Pattern | Severity |
|---------|----------|
| Auth filter not declared in the `@SecurityComponent` registry | HIGH |
| Crypto operation not declared in the `@CryptoOperation` registry (for FIPS audit) | HIGH |
| Customer-data accessor not wrapped in `@RegulatedDataAccessor` (for audit trail) | HIGH |
| External-service call not declared in `@ExternalDependency` | MEDIUM |

### 5. Crypto primitives + key lifetimes

| Pattern | Severity |
|---------|----------|
| MD5 / SHA-1 used for security purposes (not just integrity checksums) | CRITICAL |
| DES / 3DES anywhere | CRITICAL |
| AES key < 256 bits in new code | HIGH |
| Hard-coded key material in source | CRITICAL |
| Symmetric key used past declared rotation lifetime | HIGH |

## Workflow

1. **Identify the code snippet** (file path + range, or pasted snippet).
2. **Walk each check category** against the snippet.
3. **Cite the internal standard section** per finding (numbered citations to the org's actual secure-coding standard document).
4. **Produce findings** with severity + remediation + standard reference.

## Output structure

```markdown
# Secure Coding Check — {file or snippet}

## Summary
- Findings: {N}
- By severity: ...

## Findings
[per finding: rule, severity, line, snippet, standard reference, remediation]

## Sources
{linked vault notes, standard sections}
```

## Composes with

- [`codeql-pattern-finder`](../codeql-pattern-finder/SKILL.md) — when a check would benefit from being encoded as a CodeQL query for at-scan-time enforcement.
- [`secure-design-reviewer`](../secure-design-reviewer/SKILL.md) — at the design level rather than implementation.

## Acceptance test (for step 27 done-criteria)

5 categories documented with ≥20 named checks (the actual org standard will have hundreds; this is the categorization + sample). Live exercise against a specific snippet deferred to first invocation.
