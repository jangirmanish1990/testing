"""Tests for the orchestrator pipeline. All external calls are mocked so tests
run offline and deterministically (see write-test skill)."""
import pytest

from app.agents import orchestrator
from app.schemas import CriticVerdict, Finding, ResearchResult


@pytest.fixture
def fake_finding() -> Finding:
    return Finding(
        claim="The sky appears blue due to Rayleigh scattering.",
        source_url="https://example.com/rayleigh",
        source_title="Rayleigh scattering",
        confidence="high",
    )


@pytest.mark.asyncio
async def test_run_pipeline_happy_path(monkeypatch, fake_finding):
    async def fake_research(subtopic):
        return ResearchResult(subtopic=subtopic, findings=[fake_finding])

    async def fake_write(topic, findings, note=""):
        return "# T\n## Summary\nx\n## Sources\n1. [a](https://a) — note"

    async def fake_critique(draft):
        return CriticVerdict(verdict="pass", summary="looks good")

    monkeypatch.setattr(orchestrator.researcher, "research", fake_research)
    monkeypatch.setattr(orchestrator.writer, "write_report", fake_write)
    monkeypatch.setattr(orchestrator.critic, "critique", fake_critique)

    report = await orchestrator.run_pipeline("why is the sky blue")

    assert report.topic == "why is the sky blue"
    assert "Sources" in report.markdown
    assert report.source_count == 1


@pytest.mark.asyncio
async def test_run_pipeline_empty_topic_raises():
    with pytest.raises(ValueError):
        await orchestrator.run_pipeline("")


@pytest.mark.asyncio
async def test_pipeline_revises_then_stops(monkeypatch, fake_finding):
    calls = {"write": 0, "critique": 0}

    async def fake_research(subtopic):
        return ResearchResult(subtopic=subtopic, findings=[fake_finding])

    async def fake_write(topic, findings, note=""):
        calls["write"] += 1
        return "# T\n## Sources\n1. [a](https://a)"

    async def fake_critique(draft):
        calls["critique"] += 1
        return CriticVerdict(verdict="revise", summary="needs work")

    monkeypatch.setattr(orchestrator.researcher, "research", fake_research)
    monkeypatch.setattr(orchestrator.writer, "write_report", fake_write)
    monkeypatch.setattr(orchestrator.critic, "critique", fake_critique)

    await orchestrator.run_pipeline("topic")

    # Always-revise should stop at MAX_REVISIONS, not loop forever.
    assert calls["critique"] == orchestrator.MAX_REVISIONS


def test_count_sources_parses_numbered_list():
    md = "## Summary\nx\n## Sources\n1. a\n2. b\n3. c\n"
    assert orchestrator._count_sources(md) == 3
