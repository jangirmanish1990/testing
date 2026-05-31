"""Writer agent node.

Turns merged findings into a structured Markdown report following the
format-report skill schema. Never introduces facts not in the findings.
"""
import logging

from langchain_anthropic import ChatAnthropic

from app.config import get_settings
from app.schemas import Finding

log = logging.getLogger(__name__)

_PROMPT = """You are the Writer. Turn these sourced findings into a Markdown
report. Follow this exact structure: a top-level title, then ## Summary,
## Key findings (with ### theme subsections), ## Open questions / limitations,
and ## Sources (numbered). Every factual sentence ends with a [n] citation
marker mapping to the numbered Sources list. Do NOT invent facts.

Topic: {topic}

Findings (JSON):
{findings}

{revision_note}
Return Markdown only."""


def _model() -> ChatAnthropic:
    s = get_settings()
    return ChatAnthropic(model=s.model_name, api_key=s.anthropic_api_key, timeout=60)


async def write_report(
    topic: str, findings: list[Finding], revision_note: str = ""
) -> str:
    findings_json = "[" + ",".join(f.model_dump_json() for f in findings) + "]"
    note = f"Apply these critic fixes:\n{revision_note}\n" if revision_note else ""
    response = await _model().ainvoke(
        _PROMPT.format(topic=topic, findings=findings_json, revision_note=note)
    )
    return str(response.content).strip()
