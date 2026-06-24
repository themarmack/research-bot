---
title: Executive Preferences
created: 2026-06-23
updated: 2026-06-23
tags: [config]
source_skill: human
confidence: 3
links: []
---

# Executive Preferences

Per-audience preferences read by `executive-summary-writer`. Each H2 heading
is one audience. Bold-key fields under each heading are parsed; free-form prose
under the fields is passed verbatim to the writing prompt as "additional
context about this reader."

## How to edit

Add an H2 (`##`) section per audience you want to tune. The H2 title becomes
the audience handle (lowercased, spaces → hyphens) — so `## VP Engineering`
becomes the handle `vp-engineering`. To override, set `- **handle**: vp-eng`
explicitly under the section.

The first H2 named `Default` (case-insensitive) is **required**. It's the
fallback when no audience is specified, and named audiences fall back to its
fields when they omit one.

Field reference (everything optional except where noted; Default supplies the
fallback for missing fields):

```
- **handle**: kebab-case identifier (defaults to lowercased H2 title)
- **role**: descriptive (informational; copied into summary frontmatter)
- **length**: integer target word count (default 200)
- **format**: bullets | prose | mixed (default bullets)
- **voice**: free-text style descriptor
- **emphasize**: comma-list of what to lead with
- **avoid**: comma-list of phrases / framings / words to skip
- **special_interests**: comma-list of topics to always surface if relevant
- **sections**: comma-list of +include / -exclude optional sections.
                Recognized: bluf, why-this-matters-now, key-findings,
                implications, recommended-action, risks, next-decision-point,
                sources. The 3 mandatory sections (bluf, key-findings,
                recommended-action, sources) cannot be turned off.
```

To **pause** an audience without deleting it, wrap its H2 + body in an HTML
comment:

```
<!--
## Past Audience

- **length**: 100
-->
```

Free-form prose under the fields (paragraphs, sub-bullets) is passed verbatim
to the writing prompt. Use it for things like "always include a quantitative
datapoint," "she likes a 'what changed since last update' line," "avoid the
word 'leverage' — it's a personal pet peeve."

## Default

(Required. Used when no audience is specified, and as the field-by-field
fallback for named audiences that omit a field.)

- **length**: 200
- **format**: bullets
- **voice**: declarative, dense, forward-looking
- **emphasize**: bottom-line, recommended action
- **avoid**: hedging, jargon
- **sections**: all (default)

## CISO

- **handle**: ciso
- **role**: Chief Information Security Officer
- **length**: 150
- **format**: bullets
- **voice**: risk-forward, control-specific, audit-evidence-minded
- **emphasize**: regulatory impact (SR 11-7, FFIEC, NYDFS 500), control changes, audit-evidence implications
- **avoid**: "we should consider", "potentially", strategic narrative without specifics
- **special_interests**: SOX ITGC, NYDFS 500, model risk, supply-chain
- **sections**: +next-decision-point

Likes a "what changed since last update" line if relevant. Always include
the specific control or regulation a finding maps to.

## VP Engineering

- **handle**: vp-eng
- **role**: VP Engineering
- **length**: 250
- **format**: mixed
- **voice**: strategic, dev-experience-aware, peer-aware
- **emphasize**: developer impact, productivity metrics, peer-bank comparison
- **avoid**: deep legal jargon, regulator-citation maximalism
- **special_interests**: Copilot adoption, peer-bank AI coding moves, golden-path velocity
- **sections**: all

Always include 1 quantitative datapoint if available (acceptance rate, peer
benchmark, CVE count, etc.). Frame the "Recommended Action" as a choice
between 2-3 options rather than a single ask — they like to weigh in.

<!--
## Example Paused Audience

This whole section is commented out and won't be loaded.

- **length**: 100
-->

## Notes

This file is loaded fresh on every `executive-summary-writer` invocation.
There is no edit-time hook — invalid YAML in frontmatter, a missing `## Default`
section, or an unknown audience referenced in a summary call will surface as
a stop-and-report at invocation time.

To validate ahead of relying on it, ask Claude Code: `"list my executive
audiences"` — `executive-summary-writer.list_audiences` loads + parses + prints
each audience without writing anything.
