"""Pydantic schemas shared across the API and the agent pipeline."""
import datetime

from pydantic import BaseModel, Field


class Finding(BaseModel):
    claim: str
    source_url: str
    source_title: str = ""
    confidence: str = "medium"


class ResearchResult(BaseModel):
    subtopic: str
    findings: list[Finding] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class CriticIssue(BaseModel):
    type: str
    location: str
    fix: str


class CriticVerdict(BaseModel):
    verdict: str  # "pass" | "revise"
    issues: list[CriticIssue] = Field(default_factory=list)
    summary: str = ""


class Report(BaseModel):
    topic: str
    markdown: str
    source_count: int = 0


class RunSummary(BaseModel):
    id: str
    topic: str
    source_count: int
    status: str
    created_at: datetime.datetime
