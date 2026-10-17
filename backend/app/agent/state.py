"""State representation for the Project Atlas Agent Workflow."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.api.schemas import Citation, Conflict, DerivedValue


class AgentState(BaseModel):
    client_id: str
    question: str
    request_id: str
    conversation_id: Optional[str] = None
    
    # Security & Entitlements
    authorized_reports: List[str] = Field(default_factory=list)
    is_client_valid: bool = True
    
    # Classification / Intent
    intent: str = "factual"  # factual, comparison, calculation, sql_aggregate, out_of_scope, unsafe
    intent_reason: Optional[str] = None
    
    # Evidence & Tools
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    retrieved_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    sql_result: Optional[Dict[str, Any]] = None
    
    # Analytical outputs
    derived_values: List[DerivedValue] = Field(default_factory=list)
    conflicts: List[Conflict] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    
    # Quality & Escalation
    confidence: float = 1.0
    critic_notes: List[str] = Field(default_factory=list)
    escalated: bool = False
    escalation_reason: Optional[str] = None
    ticket_id: Optional[str] = None
    
    # Final response
    answer: str = ""
