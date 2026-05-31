---
name: write-test
description: >
  Use whenever you add or change a module in backend/app/. Defines how tests are
  written in this project so the Stop hook's pytest gate passes. Covers naming,
  async patterns, fixtures, and how to mock the model and MCP calls.
---

# Writing tests

Every module `backend/app/<name>.py` (or `backend/app/<pkg>/<name>.py`) has a
matching `backend/tests/test_<name>.py`.

## Conventions

- Use `pytest` + `pytest-asyncio`. Async tests are decorated `@pytest.mark.asyncio`.
- One test class or function group per public function.
- Name tests `test_<thing>_<condition>_<expected>()`, e.g.
  `test_orchestrator_empty_topic_raises()`.

## Mock external calls — never hit the network in tests

- Mock the Anthropic client and MCP tool calls with `unittest.mock` /
  `monkeypatch`. Tests must run offline and deterministically.
- Provide canned findings/draft fixtures in `backend/tests/fixtures/`.

## Example

```python
import pytest
from unittest.mock import AsyncMock

from app.agents.orchestrator import run_pipeline


@pytest.mark.asyncio
async def test_run_pipeline_returns_report(monkeypatch):
    fake_researcher = AsyncMock(return_value={"findings": [], "gaps": []})
    monkeypatch.setattr("app.agents.orchestrator.researcher", fake_researcher)

    result = await run_pipeline("test topic")

    assert "Sources" in result.markdown
    fake_researcher.assert_awaited()
```

## What to cover

- Happy path (valid input → expected shape).
- Edge cases (empty topic, no findings, critic returns `revise`).
- Error handling (model timeout, MCP unavailable → graceful failure, not crash).

Run `make test` (or `pytest`) before finishing. The Stop hook enforces this.
