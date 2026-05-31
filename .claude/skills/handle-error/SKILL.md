---
name: handle-error
description: >
  Use when writing code that calls the model, MCP servers, the database, or the
  web. Defines the project's standard patterns for retries, timeouts, graceful
  degradation, and how errors surface to the WebSocket client.
---

# Error handling patterns

External calls (model, MCP, DB, web) fail. Handle them the same way everywhere.

## Principles

1. **Never let one failed sub-agent kill the whole run.** A Researcher that
   fails on one sub-topic returns an empty `findings` with the error in `gaps`;
   the pipeline continues with the rest.
2. **Time-box every external call.** Wrap in `asyncio.wait_for` with a sensible
   timeout (model: 60s, web fetch: 20s, DB: 10s).
3. **Retry transient failures, not logical ones.** Retry on network/5xx/timeouts
   (max 2, exponential backoff). Do not retry on 4xx or validation errors.
4. **Surface, don't swallow.** Log the full error server-side; send the client a
   short, safe message over the WebSocket (`{"type": "error", "message": "..."}`).

## Reference snippet

```python
import asyncio
import logging

log = logging.getLogger(__name__)


async def with_retries(coro_factory, *, attempts=3, timeout=30.0):
    delay = 1.0
    for i in range(attempts):
        try:
            return await asyncio.wait_for(coro_factory(), timeout=timeout)
        except (asyncio.TimeoutError, ConnectionError) as exc:
            log.warning("transient failure (%s/%s): %s", i + 1, attempts, exc)
            if i == attempts - 1:
                raise
            await asyncio.sleep(delay)
            delay *= 2
```

## Client-facing errors

Never send stack traces or secrets to the browser. Map internal errors to one of:
`"search unavailable"`, `"model timeout, retrying"`, `"could not save run"`.
