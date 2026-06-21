---
title: Email Distribution
created: 2026-06-21
updated: 2026-06-21
tags: [config]
source_skill: human
confidence: 3
links: []
---

# Email Distribution

Everyone listed below receives:

- **Every scheduled digest** when its job fires (no per-digest opt-in needed).
- **Any research note** you choose to forward — you'll be asked `[y/n]` per note before it sends.

## How to edit

Add a bullet per recipient. The skill extracts any email-shaped string from
bullet lines, so all of these formats work:

- `you@gmail.com`
- `you@gmail.com — Self (optional note after the em-dash is ignored)`
- `Alice <alice@example.com>`
- `alice@example.com, bob@example.com` (both extracted from one bullet)

To **pause** an entry without deleting, wrap the bullet in an HTML comment:

```
<!-- - paused.person@example.com — out on PTO until July -->
```

Prose mentions of an email **outside** a bullet are ignored — you can write
whatever notes you want above or below the list.

## Recipients

- you@gmail.com — Self (always include this — useful for verification + your own copy)
- vp.eng@example.com — VP Eng
- ciso@example.com — CISO

## Notes

This file is loaded fresh on every email-sender invocation. There is no
edit-time hook — invalid YAML in frontmatter or zero parsed recipients will
surface at the next scheduled-digest fire as `email_failed=<reason>`. The
digest itself still lands in the vault; only the send fails.

To validate ahead of the next run, ask Claude Code: `"show me my email
distribution list"` — `email-sender.show_list` loads + parses + prints the
current recipients without sending anything.
