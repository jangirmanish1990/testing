---
description: Run the pre-deploy checks and deploy script, then verify health.
---

Deploy the application safely.

1. Run `make lint` and `make test`. If either fails, stop and report — do not deploy.
2. Confirm we are on a feature branch with a clean working tree (`git status`).
   If there are uncommitted changes, list them and stop.
3. Run `make deploy` (this pushes to the connected Render/Railway + Vercel
   projects via their CLIs / git integration).
4. Poll the backend health endpoint (`/healthz`) up to 10 times with a short
   delay until it returns 200, or report failure.
5. Print the deployed URLs and the health check result.

Never run this against `main` without an open, reviewed PR.
