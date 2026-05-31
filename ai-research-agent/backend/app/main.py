"""FastAPI application: REST + WebSocket streaming for the research agent."""
import logging

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import run_pipeline
from app.config import get_settings
from app.db import get_session, init_db
from app.models import ResearchRun
from app.schemas import RunSummary

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title="AI Research Agent", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    await init_db()


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.get("/api/runs", response_model=list[RunSummary])
async def list_runs(session: AsyncSession = Depends(get_session)) -> list[RunSummary]:
    rows = await session.scalars(
        select(ResearchRun).order_by(ResearchRun.created_at.desc()).limit(50)
    )
    return [
        RunSummary(
            id=r.id,
            topic=r.topic,
            source_count=r.source_count,
            status=r.status,
            created_at=r.created_at,
        )
        for r in rows
    ]


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str, session: AsyncSession = Depends(get_session)) -> dict:
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


@app.websocket("/ws/research")
async def research_ws(websocket: WebSocket) -> None:
    """Client sends {"topic": "..."}; server streams progress then the report."""
    await websocket.accept()
    try:
        msg = await websocket.receive_json()
        topic = (msg or {}).get("topic", "").strip()
        if not topic:
            await websocket.send_json({"type": "error", "message": "empty topic"})
            await websocket.close()
            return

        async def emit(event: str, payload: dict) -> None:
            await websocket.send_json({"type": "progress", "event": event, **payload})

        report = await run_pipeline(topic, emit=emit)

        # Persist the run.
        async for session in get_session():
            run = ResearchRun(
                topic=topic,
                report_markdown=report.markdown,
                source_count=report.source_count,
            )
            session.add(run)
            await session.commit()
            run_id = run.id
            break

        await websocket.send_json(
            {
                "type": "report",
                "run_id": run_id,
                "topic": topic,
                "markdown": report.markdown,
                "source_count": report.source_count,
            }
        )
    except WebSocketDisconnect:
        logging.info("client disconnected")
    except Exception as exc:  # noqa: BLE001
        logging.exception("pipeline error")
        await websocket.send_json({"type": "error", "message": str(exc)})
    finally:
        await websocket.close()
