# Stack reference (injected memory)

Exact versions and import patterns. Keep this in sync with requirements.txt and
package.json so generated code matches what's installed.

## Backend (Python 3.11+)

- fastapi, uvicorn[standard]      — API + ASGI server
- langgraph, langchain-anthropic  — agent state machine + model
- anthropic                       — direct SDK where LangGraph isn't needed
- sqlalchemy[asyncio], asyncpg    — async DB access to Neon
- alembic                         — schema migrations
- pydantic, pydantic-settings     — schemas + typed config
- httpx                           — async HTTP for web fetches
- pytest, pytest-asyncio          — tests
- ruff                            — lint + format

Import style:
```python
from fastapi import FastAPI, WebSocket
from langgraph.graph import StateGraph
from langchain_anthropic import ChatAnthropic
```

## Frontend

- react 18, react-dom 18
- vite (build/dev)
- tailwindcss
- No state library — `useState`/`useReducer` is enough for this app.

## Database

Neon serverless PostgreSQL. Connection string in `DATABASE_URL`. Use the
`postgresql+asyncpg://` driver prefix for SQLAlchemy async.

## Model

`claude-sonnet` family via `langchain_anthropic.ChatAnthropic` (or the raw
`anthropic` SDK inside the custom MCP server).
