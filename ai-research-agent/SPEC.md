# SPEC.md — AI Research Agent

> This is the north-star document. Claude Code reads this at the start of every
> session. Keep it accurate; if scope changes, update this file first.

## 1. Purpose

An **autonomous research assistant**. The user submits a topic; the system
searches the web, synthesizes findings across sources, critiques its own draft
for gaps and hallucinations, and produces a structured, citation-backed report.

The project's secondary purpose is to demonstrate end-to-end use of **every
major Claude Code feature** (spec, memory, rules, sub-agents, MCP servers,
hooks, skills, custom commands, headless mode) on a real, deployable app.

## 2. What "done" looks like

A user can:
1. Open a web dashboard and type a research topic.
2. Watch the multi-agent pipeline stream its progress in real time.
3. Receive a structured Markdown report with inline citations.
4. See past research runs persisted in a history sidebar.
5. The whole thing runs on free-tier cloud infrastructure.

## 3. Architecture (high level)

```
User → React dashboard → FastAPI (WebSocket) → Orchestrator
                                                   ├── Researcher agent  (web search + fetch)
                                                   ├── Writer agent      (drafts the report)
                                                   └── Critic agent      (validates, finds gaps)
                                                          ↓
                                              Neon PostgreSQL (run history)
```

The agents run as a LangGraph state machine. The Researcher and Critic can run
in parallel where the graph allows it.

## 4. Tech stack

| Layer        | Choice                                              |
|--------------|-----------------------------------------------------|
| Agent runtime| LangGraph + Anthropic Claude (claude-sonnet)        |
| Web search   | Brave Search MCP server                             |
| Backend      | FastAPI + WebSocket streaming, SQLAlchemy (async)   |
| Database     | Neon (serverless PostgreSQL, free tier)             |
| Frontend     | React + Vite + Tailwind                             |
| Observability| LangSmith tracing                                   |
| Deploy       | Render/Railway (API) + Vercel/Netlify (frontend)    |

## 5. Constraints

- **Development is on Windows without admin rights, Docker, or local Postgres.**
  Use Neon for the database; use the Makefile / npm scripts for dev tasks.
- Keep secrets in `.env` (never commit). See `backend/.env.example`.
- Every new Python module needs a matching `tests/test_*.py`.
- The agent must always cite its sources; uncited claims are a defect.

## 6. Out of scope (for v1)

- Authentication / multi-user accounts (single-user demo is fine).
- PDF/file upload as a research source (web only for now).
- Fine-tuning or self-hosting models.

## 7. Milestones

- **M1** — Spec, rules, repo scaffold, MCP wired up.
- **M2** — Working agent pipeline in headless mode (`claude --print "/research ..."`).
- **M3** — FastAPI + WebSocket streaming.
- **M4** — React dashboard with live streaming + history.
- **M5** — Deployed to free cloud + GitHub Actions CI.
