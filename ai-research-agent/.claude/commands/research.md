---
description: Run the full multi-agent research pipeline on a topic.
argument-hint: <topic>
---

Run the complete research pipeline for the topic: **$ARGUMENTS**

Steps:

1. Split the topic into 3–5 focused sub-topics.
2. For each sub-topic, dispatch a `researcher` sub-agent **in parallel** (use the
   Task tool, one call per sub-topic in a single message so they run concurrently).
3. Collect all findings JSON and merge them, de-duplicating overlapping claims.
4. Dispatch the `writer` sub-agent with the merged findings to produce a draft
   report following `.claude/skills/format-report/SKILL.md`.
5. Dispatch the `critic` sub-agent on the draft.
   - If verdict is `revise`, send the issues back to the `writer` and re-run the
     `critic`. Loop at most twice.
   - If verdict is `pass`, continue.
6. Save the final report to `reports/<slugified-topic>.md`.
7. Persist a record of this run (topic, timestamp, report path, source count) to
   the database via the `research-db` MCP server.
8. Print a one-paragraph summary of what was produced and where it was saved.
