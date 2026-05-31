"""Custom MCP server: 'research-db'.

Exposes the project's research-run history to Claude Code as MCP tools, so the
agent can save and recall past runs. Built on the lightweight FastMCP API.

Run standalone:  python backend/app/mcp/neon_mcp_server.py
Claude Code launches it automatically via the entry in .claude/settings.json.

Tools exposed:
  - save_run(topic, report_markdown, source_count) -> run_id
  - list_runs(limit=20)                             -> [ {id, topic, ...} ]
  - get_run(run_id)                                 -> full record
"""
import asyncio
import os

from mcp.server.fastmcp import FastMCP
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Reuse the app's models so schema stays in one place.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.db import Base  # noqa: E402
from app.models import ResearchRun  # noqa: E402

mcp = FastMCP("research-db")

_engine = create_async_engine(
    os.environ.get("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/research")
)
_Session = async_sessionmaker(_engine, expire_on_commit=False)


async def _ensure_schema() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@mcp.tool()
async def save_run(topic: str, report_markdown: str, source_count: int = 0) -> str:
    """Persist a completed research run. Returns the new run id."""
    async with _Session() as session:
        run = ResearchRun(
            topic=topic, report_markdown=report_markdown, source_count=source_count
        )
        session.add(run)
        await session.commit()
        return run.id


@mcp.tool()
async def list_runs(limit: int = 20) -> list[dict]:
    """List recent research runs (most recent first)."""
    async with _Session() as session:
        rows = await session.scalars(
            select(ResearchRun).order_by(ResearchRun.created_at.desc()).limit(limit)
        )
        return [
            {
                "id": r.id,
                "topic": r.topic,
                "source_count": r.source_count,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]


@mcp.tool()
async def get_run(run_id: str) -> dict:
    """Fetch the full report for a given run id."""
    async with _Session() as session:
        run = await session.get(ResearchRun, run_id)
        if run is None:
            return {"error": "not found"}
        return {
            "id": run.id,
            "topic": run.topic,
            "report_markdown": run.report_markdown,
            "source_count": run.source_count,
            "created_at": run.created_at.isoformat(),
        }


if __name__ == "__main__":
    asyncio.run(_ensure_schema())
    mcp.run()
