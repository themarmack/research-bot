---
name: codeql-pattern-finder
description: Given a vulnerability class or business rule (e.g. "find SQL injection via string concat in Java", "find calls to deprecated crypto APIs", "find unchecked PII handling at API boundaries"), search the standard github/codeql packs and community packs for an existing query that matches. If no off-the-shelf query exists, sketch a custom query in CodeQL with annotated reasoning. Output is a research note with the chosen query (or sketch) + how to deploy it via codeql-onboarding-helper. Use when planning a custom pack rollout, when an internal pattern keeps appearing in incidents, or when a regulator-specific control needs a code-level enforcement.
---

# codeql-pattern-finder

The query-discovery and query-authoring side of the CodeQL pair. Most org-specific patterns already exist as community queries; this skill finds them. When they don't, it sketches a custom query — emphasis on *sketch*, not production-ready, since custom CodeQL is a real authoring project requiring tuning.

## When to use

- A repeated incident pattern (post-mortems mention the same vulnerability class) — find or build a query.
- A regulator-specific control (e.g., PCI-DSS Req 3.4 on PAN protection) — find a query that approximates the control.
- A specific deprecation campaign (move off an internal API that's known-bad) — build a query.
- Planning a custom pack for the org — start by enumerating which patterns even need to be custom vs covered already.

## When NOT to use

- Setting up CodeQL on a repo for the first time → `codeql-onboarding-helper`.
- Triaging a specific alert — not in scope.
- Non-code-pattern questions (process / policy) — those are research, not CodeQL.

## Workflow

1. **Categorize the pattern**: vulnerability class (SQL injection, XSS, deserialization) OR business rule (specific API usage, specific data-flow constraint) OR deprecation campaign.
2. **Search the standard `github/codeql` repo** for an existing query in the relevant language pack (e.g., `java/ql/src/Security/CWE/CWE-089/SqlConcatenated.ql`).
3. **Search community packs** at `codeql-packs/*` (e.g., `codeql-packs/log4j-vuln-pack`) for ecosystem-specific patterns.
4. **If found**: document the existing query, how to invoke it (suite selection or custom pack include), and any tuning needed (additional sinks/sources for the org's specific data flow).
5. **If not found**: sketch a custom query. Use CodeQL's data-flow library for taint analysis cases; use simple predicate queries for syntactic matches.
6. **Output a research note** + a deployment plan via `codeql-onboarding-helper`.

## Custom-query sketch structure

When sketching, follow this scaffold for taint-tracking queries:

```ql
import java
import semmle.code.java.dataflow.TaintTracking

class BankSource extends DataFlow::Node { /* sources: user input, request params */ }
class BankSink extends DataFlow::Node { /* sinks: dangerous APIs */ }

module BankFlowConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) { source instanceof BankSource }
  predicate isSink(DataFlow::Node sink) { sink instanceof BankSink }
}
module BankFlow = TaintTracking::Global<BankFlowConfig>;

from DataFlow::Node source, DataFlow::Node sink
where BankFlow::flow(source, sink)
select sink, source, sink, "Tainted flow from $@", source, "user input"
```

For syntactic-match queries (e.g., "any call to `LegacyAuth.signWith(...)`"), the scaffold is simpler — just `from Method m where m.getName() = "..."` plus context.

**Always include**: language pragma at top, query metadata (`@name`, `@description`, `@severity`), and a sample positive + negative case so the query is testable.

## Output

`vault/research/github/YYYY-MM-DD-codeql-pattern-{slug}.md` — research note with the chosen query (or sketch), references to the source query in the standard pack (if it exists), and a "to deploy" section.

## Composes with

- [`codeql-onboarding-helper`](../codeql-onboarding-helper/SKILL.md) — the deploy mechanism for queries discovered or authored here.
- `vault-querier` — find prior pattern-finder runs to avoid duplicate work.
- `ghas-feature-research` (planned) — when GitHub adds new CodeQL features (e.g., autofix, AI-assisted query generation) that change the discovery process.

## Acceptance test (for step 19 done-criteria)

Produce one research note for a specific pattern (e.g., "Java SQL injection via string concat"). Confirm the note identifies the existing standard-pack query (if any), how to enable it, and the org-specific tuning recommended.
