# Fabricated claim — for verify-claim acceptance test

This file documents the input shape for testing the kill-on-refute path.

## Test input

```json
{
  "claim": "GitHub Copilot Enterprise now ships natively in COBOL and runs on z/OS mainframes without any translation layer.",
  "quoted_anchor": "Copilot Enterprise has been rewritten in COBOL for native z/OS deployment.",
  "source_url": "https://example.com/fabricated",
  "source_tier": 3,
  "claim_type": "fact",
  "entities": ["copilot"],
  "confidence_hint": 1
}
```

## Why this is the right test fixture

- Specific enough to be falsifiable.
- Obviously contradicted by every legitimate source on Copilot's actual architecture.
- Tier-3 source (matches how unsourced/poorly-sourced claims look).
- Tests that verifiers actively search for refuting evidence rather than rubber-stamping.

## Expected verdict

```
verdict: killed
votes: 3
refute_count: 3 (or 2 minimum)
confirm_count: 0 (or ≤1)
recommended_confidence: 1
```

Each verifier should produce evidence like: "No GitHub blog post, changelog entry, documentation, or third-party source confirms Copilot is written in COBOL or runs on z/OS." That's a refutation by absence of confirmation — perfectly valid against a fabricated claim.

## Implementation note

When `verify-claim` is first invoked for real (step 11 — `copilot-deep-dive`), exercise this fixture as the first invocation to confirm the 3-Agents-in-parallel + ≥2/3-refute path works end to end before letting it gate real promotes.
