---
name: format-report
description: >
  Use when producing or validating a research report. Defines the exact Markdown
  structure, citation style, and section order every report must follow. The
  Writer agent must follow it; the Critic agent checks against it.
---

# Report format

Every research report follows this exact structure.

## Required structure

```markdown
# <Topic Title>

*Generated <YYYY-MM-DD> · <N> sources*

## Summary

A 3–5 sentence executive summary. No citations needed here — it distills the
sourced material below.

## Key findings

### <Theme 1>

Prose with inline citations. Every factual sentence ends with a marker like [1].
Multiple sources: [1][3].

### <Theme 2>

...

## Open questions / limitations

- Bullet list of gaps, contested points, or things sources disagreed on.

## Sources

1. [Source title](https://full-url) — one-line note on what it supports.
2. ...
```

## Rules

- Section order is fixed: Summary → Key findings → Limitations → Sources.
- Citation markers are square-bracketed integers `[n]` that map 1:1 to the
  numbered Sources list.
- Never cite a source that isn't in the list; never list a source you don't cite.
- Use `###` for themes inside Key findings; don't go deeper than `###`.
- Dates in ISO format (`2025-05-31`).
- Keep paragraphs short (2–4 sentences). Neutral, factual tone.
