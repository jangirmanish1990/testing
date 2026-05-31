"""Orchestrator — the LangGraph state machine that runs the pipeline.

Flow:  plan -> research (fan-out per sub-topic) -> write -> critique
         -> (revise loop, max 2) -> done

It streams progress events via an optional async callback so the FastAPI
WebSocket layer can push updates to the browser in real time.
"""
import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents import critic, researcher, writer
from app.schemas import CriticVerdict, Finding, Report

log = logging.getLogger(__name__)

# Progress callback signature: async (event_type, payload) -> None
Emitter = Callable[[str, dict], Awaitable[None]]

MAX_REVISIONS = 2


def _merge(existing: list, incoming: list) -> list:
    return (existing or []) + (incoming or [])


class PipelineState(TypedDict, total=False):
    topic: str
    subtopics: list[str]
    findings: Annotated[list[Finding], _merge]
    draft: str
    verdict: CriticVerdict
    revisions: int
    emit: Emitter


async def _emit(state: PipelineState, event: str, payload: dict) -> None:
    cb = state.get("emit")
    if cb:
        await cb(event, payload)


async def plan_node(state: PipelineState) -> dict:
    topic = state["topic"]
    if not topic or not topic.strip():
        raise ValueError("topic must not be empty")
    # A simple heuristic split; a real version asks the model to decompose.
    subtopics = [
        f"{topic} — overview and definitions",
        f"{topic} — current state and recent developments",
        f"{topic} — challenges, criticism, and open questions",
    ]
    await _emit(state, "plan", {"subtopics": subtopics})
    return {"subtopics": subtopics, "revisions": 0}


async def research_node(state: PipelineState) -> dict:
    await _emit(state, "research_start", {"count": len(state["subtopics"])})
    # Fan out: run all sub-topic researchers concurrently.
    results = await asyncio.gather(
        *(researcher.research(st) for st in state["subtopics"])
    )
    findings: list[Finding] = []
    for r in results:
        findings.extend(r.findings)
    await _emit(state, "research_done", {"findings": len(findings)})
    return {"findings": findings}


async def write_node(state: PipelineState) -> dict:
    note = ""
    if state.get("verdict") and state["verdict"].verdict == "revise":
        note = "\n".join(f"- [{i.type}] {i.location}: {i.fix}"
                         for i in state["verdict"].issues)
    await _emit(state, "write_start", {"revision": state.get("revisions", 0)})
    draft = await writer.write_report(state["topic"], state["findings"], note)
    await _emit(state, "write_done", {"chars": len(draft)})
    return {"draft": draft}


async def critique_node(state: PipelineState) -> dict:
    await _emit(state, "critique_start", {})
    verdict = await critic.critique(state["draft"])
    await _emit(state, "critique_done",
                {"verdict": verdict.verdict, "issues": len(verdict.issues)})
    return {"verdict": verdict, "revisions": state.get("revisions", 0) + 1}


def _route_after_critique(state: PipelineState) -> str:
    verdict = state.get("verdict")
    if verdict and verdict.verdict == "pass":
        return END
    if state.get("revisions", 0) >= MAX_REVISIONS:
        return END  # give up revising; ship best effort
    return "write"


def build_graph():
    g = StateGraph(PipelineState)
    g.add_node("plan", plan_node)
    g.add_node("research", research_node)
    g.add_node("write", write_node)
    g.add_node("critique", critique_node)
    g.add_edge(START, "plan")
    g.add_edge("plan", "research")
    g.add_edge("research", "write")
    g.add_edge("write", "critique")
    g.add_conditional_edges("critique", _route_after_critique)
    return g.compile()


_GRAPH = build_graph()


async def run_pipeline(topic: str, emit: Emitter | None = None) -> Report:
    """Run the full pipeline and return the finished report."""
    state: PipelineState = {"topic": topic}
    if emit:
        state["emit"] = emit
    final = await _GRAPH.ainvoke(state)
    sources = _count_sources(final.get("draft", ""))
    return Report(topic=topic, markdown=final.get("draft", ""), source_count=sources)


def _count_sources(markdown: str) -> int:
    in_sources = False
    count = 0
    for line in markdown.splitlines():
        if line.strip().lower().startswith("## sources"):
            in_sources = True
            continue
        if in_sources and line.strip()[:2].rstrip(".").isdigit():
            count += 1
    return count
