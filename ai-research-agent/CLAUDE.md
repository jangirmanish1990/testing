# CLAUDE.md — project rules & memory

> Claude Code loads this automatically every session. These are hard rules for
> how to work in this repository. Read `SPEC.md` for *what* we're building;
> this file is *how* to build it.

## Project summary

Autonomous multi-agent research assistant. See `SPEC.md` for full detail.
Stack: LangGraph + Claude, FastAPI + WebSocket, Neon PostgreSQL, React + Vite.

## Golden rules

1. **Read `SPEC.md` first** if you're unsure about scope or intent.
2. **Never commit secrets.** All keys live in `.env` (gitignored). When you need
   a new secret, add it to `backend/.env.example` with a placeholder value.
3. **Tests are mandatory.** Every new module in `backend/app/` must have a
   matching `backend/tests/test_<module>.py`. Run `pytest` before declaring any
   coding task complete (the Stop hook enforces this).
4. **Never push directly to `main`.** Work happens on feature branches; open a PR.
5. **The agent must cite sources.** Any factual claim in a report without a
   citation is a defect — fix it, don't ship it.
6. **Windows-friendly.** No Docker, no local Postgres, no commands that need
   admin rights. Use the `Makefile` targets (or the npm scripts in `frontend/`).

## Code conventions

- Python: 3.11+, `ruff` for lint/format, type hints on all public functions,
  `async def` for anything touching I/O (DB, HTTP, the model).
- Imports: standard lib → third-party → local, separated by blank lines.
- React: functional components + hooks only. Tailwind for styling, no inline
  style objects except for dynamic values.
- Commit messages: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`).

## Always run before finishing a task

```bash
make lint    # ruff check + format
make test    # pytest
```

## Files you should know about

- `SPEC.md` — what we're building and why.
- `.claude/settings.json` — allowed tools, MCP servers, hook wiring.
- `.claude/agents/*.md` — sub-agent role definitions.
- `.claude/commands/*.md` — custom slash commands.
- `.claude/skills/*/SKILL.md` — reusable task playbooks.
- `.claude/memory/*.md` — injected background context.
- `backend/app/agents/` — the LangGraph pipeline implementation.

## Environment

Required env vars (see `backend/.env.example`):
`ANTHROPIC_API_KEY`, `BRAVE_API_KEY`, `DATABASE_URL` (Neon), `LANGSMITH_API_KEY`.
