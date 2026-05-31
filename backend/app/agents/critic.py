"""Critic agent node.

Audits a drafted report for uncited claims, hallucinations, imbalance, gaps,
and clarity. Returns a structured verdict. A single uncited/hallucinated claim
forces a 'revise'.
"""
import json
import logging

from langchain_anthropic import ChatAnthropic

from app.config import get_settings
from app.schemas import CriticIssue, CriticVerdict

log = logging.getLogger(__name__)

_PROMPT = """You are the Critic. Audit this report. Check: every factual claim
has a [n] citation resolving to a real source; no claim exceeds its source;
contested topics are balanced; no major gap; clear prose. A single uncited or
hallucinated claim => verdict "revise".

Return STRICT JSON only:
{{"verdict": "pass|revise", "issues": [{{"type": "uncited|hallucination|
imbalance|gap|clarity", "location": "...", "fix": "..."}}], "summary": "..."}}

Report:
{report}"""


def _model() -> ChatAnthropic:
    s = get_settings()
    return ChatAnthropic(model=s.model_name, api_key=s.anthropic_api_key, timeout=60)


async def critique(report_markdown: str) -> CriticVerdict:
    try:
        response = await _model().ainvoke(_PROMPT.format(report=report_markdown))
        data = json.loads(_strip_fences(response.content))
        return CriticVerdict(
            verdict=data.get("verdict", "revise"),
            issues=[CriticIssue(**i) for i in data.get("issues", [])],
            summary=data.get("summary", ""),
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("critic failed: %s", exc)
        # Fail safe: if the critic itself breaks, ask for a revision rather than
        # silently passing a possibly-bad report.
        return CriticVerdict(verdict="revise", summary=f"critic error: {exc}")


def _strip_fences(text: str) -> str:
    return text.replace("```json", "").replace("```", "").strip()
