---
name: verify-claim
description: Adversarially verify a single load-bearing claim by spawning N independent refuters (default 3) and killing the claim at ≥2/3 refute. Returns `{verdict, vote_breakdown, evidence}`. Reusable everywhere a claim needs scrutiny — Category 1 research synthesis, memory-curator before promoting to facts/, weekly-intelligence-digest before publishing a "what changed" item. Lifted from the built-in deep-research skill's verification pattern. Composes on claim-extractor (its input shape).
---

# verify-claim

Single-claim adversarial verification. Spawn N independent verifiers each prompted to **refute** (not confirm) the claim, count refutes, and kill the claim at ≥2/3 refute. This is the pattern from the built-in `deep-research` skill (`VOTES_PER_CLAIM=3`, `REFUTATIONS_REQUIRED=2`) extracted as a reusable primitive.

The asymmetry matters: confirm-prompts find confirming evidence too easily; refute-prompts surface the failure modes that would kill the claim if real.

## When to use

- A Category 1 research skill has a load-bearing claim it wants to publish (in a research note or fact) and needs confidence > 2.
- `memory-curator` is about to promote a fact to `facts/{entity}/{predicate}.md` from an `_inbox/` candidate — verify first to avoid persisting fabricated content.
- A scheduled-agent digest's "what changed" item needs validation before publishing (e.g., regulator-watch claims about a new SR letter).

## When NOT to use

- Claims from tier-1 vendor primary sources where the source IS the authority (e.g., GitHub's own changelog claiming a Copilot feature shipped — the changelog is definitive; no external refutation possible).
- Trivial claims that aren't load-bearing for any downstream action.
- Claims already verified within the last 24 hours (cache via `seen-tracker` later; for now, dedupe on `(claim, source_url)` within session).

## Input

A single claim in the schema produced by `claim-extractor`:

```json
{
  "claim": "Copilot Enterprise audit log now exports to S3 with KMS encryption.",
  "quoted_anchor": "Audit log now exports to S3 with KMS encryption (previously CSV download only).",
  "source_url": "https://example.com/article",
  "source_tier": 1,
  "claim_type": "fact",
  "entities": ["copilot"],
  "confidence_hint": 2
}
```

Optional config:
- `votes` — number of independent verifiers (default `3`)
- `refute_threshold` — minimum refutes to kill the claim (default `2`, i.e. ≥2/3)
- `time_budget_seconds` — soft cap per verifier (default `90`)

## Workflow

1. **Spawn N verifiers in parallel** via the `Agent` tool (general-purpose subagent type, or `claude` if available). Each gets the same prompt template:

   > "You are an adversarial fact-checker. Your job is to **refute** the following claim. Default to refuted=true if uncertain. Use web search to find any source that contradicts, qualifies, post-dates, or undermines the claim. Return JSON: `{refuted: bool, evidence: string, confidence: 1-3, contradicting_urls: [string]}`."
   >
   > "Claim: <claim>"
   > "Source: <source_url> (tier <source_tier>)"
   > "Original anchor: <quoted_anchor>"

   The "default to refuted=true if uncertain" line is load-bearing — it counteracts the confirmation-bias tendency of LLMs to look for supporting evidence.

2. **Collect votes**. Each verifier returns `{refuted, evidence, confidence, contradicting_urls}`.

3. **Tally**:
   - Count `refuted == true` votes.
   - If ≥ `refute_threshold`, **verdict: killed**.
   - Else **verdict: survived**.

4. **Edge handling**:
   - Agent failure (timeout / error): count as **abstention** (not a vote in either direction). If 2+ verifiers abstain, return `verdict: inconclusive` — caller should retry or downgrade the claim's `confidence` without killing.
   - Conflicting evidence (some refute, some confirm with strong evidence): still apply the threshold; `verdict: survived` with `dispute: true` flag set, and tag the persisted fact with `#disputed`.

## Output shape

```json
{
  "claim": "<copied from input>",
  "verdict": "survived | killed | inconclusive",
  "votes": 3,
  "refute_count": 1,
  "confirm_count": 2,
  "abstentions": 0,
  "dispute": false,
  "vote_breakdown": [
    {
      "voter": "verifier-1",
      "refuted": false,
      "confidence": 3,
      "evidence": "GitHub changelog confirms the S3 export feature shipped 2026-05-14.",
      "contradicting_urls": []
    },
    {
      "voter": "verifier-2",
      "refuted": true,
      "confidence": 2,
      "evidence": "GitHub docs page lists S3 export as 'preview' not GA — claim should be qualified.",
      "contradicting_urls": ["https://docs.github.com/..."]
    },
    {
      "voter": "verifier-3",
      "refuted": false,
      "confidence": 3,
      "evidence": "Multiple secondary sources confirm.",
      "contradicting_urls": []
    }
  ],
  "recommended_confidence": 2,
  "recommended_tags_addition": []
}
```

- **`recommended_confidence`**: 3 if survived unanimously, 2 if survived with dispute, 1 if killed or inconclusive.
- **`recommended_tags_addition`**: `["#disputed"]` if `dispute: true`; `["#unverified"]` if inconclusive.

## Failure modes — surface, not swallow

Per the stop-and-report guardrail:
- All-3 verifier failures → return `verdict: inconclusive` with `abstentions: 3` and an explanation; **never default to survived** on infrastructure failure.
- Verifier returns malformed JSON → count as abstention, log raw response in `vote_breakdown`.
- Time budget exceeded → return whatever votes completed; if < 2 valid votes, `verdict: inconclusive`.

## Composes with

- [`claim-extractor`](../claim-extractor/SKILL.md) — its output items are this skill's input.
- `memory-curator` — calls this before promoting facts.
- Built-in `deep-research` skill — same pattern; this is the extracted primitive.

## Acceptance test (for step 5 done-criteria)

Run on `tests/fabricated-claim.md` (in this skill folder). The fixture contains a fabricated claim about a non-existent feature. Expected:

- `votes: 3`, `refute_count: ≥2`, `verdict: killed`.
- `recommended_confidence: 1`.
- `vote_breakdown` has 3 entries with `refuted: true` and contradicting-URL evidence (or a "no evidence found supporting this exists" abstention pattern — both kill the claim).

This is a network-dependent test; document the spawn-3-Agents-in-parallel pattern as the implementation and exercise it for real on step 11 (`copilot-deep-dive` + `github-platform-watch`) when verify-claim is first invoked in anger.
