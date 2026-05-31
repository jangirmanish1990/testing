# AI Research Agent

An autonomous, multi-agent research assistant — and a reference project that
exercises **every major Claude Code feature**. Give it a topic; it searches the
web, synthesizes findings, critiques its own draft, and returns a structured,
citation-backed report. Built to run on free-tier cloud infrastructure.

## How the agents work

```
topic → plan → research (parallel per sub-topic) → write → critique
                                                       ↑________│ (revise, max 2)
                                                                ↓
                                                      structured report + history
```

Three specialised agents, each with a single job:
- **Researcher** gathers sourced facts (no prose).
- **Writer** arranges facts into a report (no new facts).
- **Critic** adversarially audits for uncited claims, hallucinations, and gaps.

## Claude Code features used

| Feature | File(s) |
|---|---|
| Spec | `SPEC.md` |
| Project rules & memory | `CLAUDE.md` |
| Injected memory | `.claude/memory/*.md` |
| Tool permissions | `.claude/settings.json` (`permissions`) |
| MCP servers | `.claude/settings.json` (`mcpServers`) + `backend/app/mcp/neon_mcp_server.py` (custom) |
| Sub-agents | `.claude/agents/{researcher,writer,critic}.md` |
| Custom commands | `.claude/commands/{research,review,deploy}.md` |
| Skills | `.claude/skills/*/SKILL.md` |
| Hooks (Pre/Post/Stop) | `.claude/hooks/*.py` |
| Headless mode | `.github/workflows/ci.yml` (`claude --print …`) |

## Prerequisites

- Python 3.11+, Node 20+
- A [Neon](https://neon.tech) database (free), an Anthropic API key, a Brave
  Search API key. Copy `backend/.env.example` → `backend/.env` and fill it in.

> Windows note: no Docker or local Postgres needed. Neon is hosted; all dev
> tasks run through `make` targets (or run the commands in the Makefile directly
> if you don't have `make`).

## Quick start

```bash
make install            # backend + frontend deps

# terminal 1 — API
make dev                # uvicorn on :8000

# terminal 2 — frontend
make front              # vite on :5173
```

Open http://localhost:5173, type a topic, watch it stream.

## Driving it with Claude Code

```bash
claude                                  # interactive
> /research large language model safety # full pipeline
> /review                               # critic on latest report
> /deploy                               # checks + deploy

claude --print "/research quantum error correction"   # headless / scriptable
```

## Build order (the roadmap)

1. **M1** — `SPEC.md`, `CLAUDE.md`, `.claude/` scaffold, MCP wired.
2. **M2** — agent pipeline (`backend/app/agents/`) working in headless mode.
3. **M3** — FastAPI + WebSocket (`backend/app/main.py`).
4. **M4** — React dashboard (`frontend/`).
5. **M5** — deploy: backend on Render (`render.yaml`) or Railway (`Procfile`),
   frontend on Vercel (`frontend/vercel.json`), CI in `.github/workflows/ci.yml`.

## Tests

```bash
make test     # pytest; the Stop hook runs this before any task is "done"
```

## License

MIT — it's a portfolio project, use it freely.
