---
description: Run the critic agent on the most recent report draft.
argument-hint: [report-path]
---

Review a research report for quality and correctness.

1. If a path was given in $ARGUMENTS, use it. Otherwise, find the most recently
   modified file in `reports/`.
2. Dispatch the `critic` sub-agent on that report.
3. Print the critic's verdict and the full list of issues.
4. If the verdict is `revise`, ask whether I want you to dispatch the `writer`
   to apply the fixes now.
