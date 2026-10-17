"""Pydantic schemas and typed request/response contracts for Project Atlas."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    client_id: str = Field(..., description="Authenticated client identifier (e.g., C-01, C-02)")
    question: str = Field(..., min_length=1, max_length=2000, description="Market research question")
    conversation_id: Optional[str] = Field(None, description="Optional persistent conversation identifier")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional validated session context")

    @field_validator("question")
    @classmethod
    def validate_non_empty_question(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Question cannot be empty or whitespace only.")
        return stripped


class Citation(BaseModel):
    report_id: str = Field(..., description="Report identifier (e.g., R-101)")
    report_title: str = Field(..., description="Report title")
    page: int = Field(..., description="Source page number")
    excerpt: str = Field(..., description="Verifiable supporting text excerpt")
    metric: Optional[str] = Field(None, description="Market metric or claim supported")


class Conflict(BaseModel):
    topic: str = Field(..., description="Contradiction topic (e.g., 2024 Market Size)")
    sources: List[str] = Field(..., description="Contradicting report IDs")
    discrepancy: str = Field(..., description="Description of the conflicting figures")
    scope_explanation: str = Field(..., description="Underlying scope, methodology, or window differences")


class DerivedValue(BaseModel):
    metric: str = Field(..., description="Name of the computed metric")
    formula: str = Field(..., description="Exact mathematical formula used")
    inputs: Dict[str, Any] = Field(..., description="Input parameters and base figures")
    assumptions: str = Field(..., description="Explicit methodological assumptions")
    result: str = Field(..., description="Computed numerical result with unit")
    sources: List[str] = Field(default_factory=list, description="Source reports supporting base inputs")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Evidence-grounded research copilot answer")
    citations: List[Citation] = Field(default_factory=list, description="Verifiable citations for all claims")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Rule-based or calibrated confidence score")
    conflicts: List[Conflict] = Field(default_factory=list, description="Identified source contradictions and scope notes")
    derived_values: List[DerivedValue] = Field(default_factory=list, description="Transparent mathematical derivations")
    escalated: bool = Field(False, description="True if question was handed over to a human analyst")
    ticket_id: Optional[str] = Field(None, description="Created escalation ticket ID if escalated")
    request_id: Optional[str] = Field(None, description="Correlation identifier for tracing")
    conversation_id: Optional[str] = Field(None, description="Conversation session ID")


class IngestRequest(BaseModel):
    reports_dir: Optional[str] = Field(None, description="Directory containing report documents to ingest")


class IngestResponse(BaseModel):
    status: str
    reports_indexed: List[str]
    chunks_created: int
    injections_detected: int
    total_chunks_in_store: int


class EscalationResponse(BaseModel):
    id: str
    client_id: str
    question: str
    reason: str
    confidence: float
    status: str
    citations_json: Optional[Any] = None
    created_at: str


class FeedbackRequest(BaseModel):
    message_id: str
    client_id: str
    rating: int = Field(..., ge=-1, le=1, description="1 for thumbs up, -1 for thumbs down")
    feedback_text: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    vector_store: str
    total_chunks: int
    configured_llm: str
    configured_embedding: str
