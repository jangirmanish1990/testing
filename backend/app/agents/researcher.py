"""Researcher agent node.

Searches the web for a sub-topic and extracts sourced factual claims. In
production this calls the Brave Search MCP + web fetch; here the model is
prompted to return strict JSON we can validate into ResearchResult.
"""
import json
import logging

from langchain_anthropic import ChatAnthropic

from app.config import get_settings
from app.schemas import Finding, ResearchResult

log = logging.getLogger(__name__)

_PROMPT = """You are the Researcher. Gather sourced facts on this sub-topic.

Sub-topic: {subtopic}

Use the search tool to find 3-5 reputable sources, then extract atomic factual
claims, each with a real source URL. Return STRICT JSON only, no prose:

{{"subtopic": "...", "findings": [{{"claim": "...", "source_url": "...",
"source_title": "...", "confidence": "high|medium|low"}}], "gaps": ["..."]}}"""


def _model() -> ChatAnthropic:
    s = get_settings()
    return ChatAnthropic(model=s.model_name, api_key=s.anthropic_api_key, timeout=60)


async def research(subtopic: str) -> ResearchResult:
    """Run the researcher on a single sub-topic. Failures degrade gracefully."""
    try:
        # In the deployed app the model is bound to the Brave Search MCP tool.
        response = await _model().ainvoke(_PROMPT.format(subtopic=subtopic))
        data = json.loads(_strip_fences(response.content))
        return ResearchResult(
            subtopic=data.get("subtopic", subtopic),
            findings=[Finding(**f) for f in data.get("findings", [])],
            gaps=data.get("gaps", []),
        )
    except Exception as exc:  # noqa: BLE001 - one bad subtopic must not kill the run
        log.warning("researcher failed for %r: %s", subtopic, exc)
        return ResearchResult(subtopic=subtopic, gaps=[f"research failed: {exc}"])


def _strip_fences(text: str) -> str:
    return text.replace("```json", "").replace("```", "").strip()
