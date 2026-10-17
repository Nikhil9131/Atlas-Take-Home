"""Escalation node: Creates real persisted MySQL tickets for uncertain questions."""

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.agent.state import AgentState
from backend.app.db.models import Escalation, AuditEvent
from backend.app.core.logging import logger


def escalation_node(state: AgentState, db: Session) -> AgentState:
    """Persists an escalation ticket to MySQL if escalation was triggered."""
    if not state.escalated:
        return state

    ticket_id = f"ESC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    state.ticket_id = ticket_id

    citations_summary = [
        {"report_id": c.report_id, "page": c.page, "metric": c.metric}
        for c in state.citations
    ]

    try:
        escalation_record = Escalation(
            id=ticket_id,
            client_id=state.client_id,
            question=state.question,
            reason=state.escalation_reason or "Low confidence / complex methodology requirement",
            confidence=float(state.confidence),
            status="open",
            citations_json=citations_summary
        )
        db.add(escalation_record)

        # Audit event
        audit_record = AuditEvent(
            event_type="ESCALATION_TICKET_CREATED",
            client_id=state.client_id,
            request_id=state.request_id,
            unsafe_flag=False,
            details={"ticket_id": ticket_id, "reason": escalation_record.reason, "confidence": state.confidence}
        )
        db.add(audit_record)
        db.commit()

        logger.info(
            f"Created escalation ticket {ticket_id} for client {state.client_id} (confidence: {state.confidence:.2f})"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to persist escalation ticket: {e}")
        # Even if DB write fails, preserve ticket ID in memory
        state.ticket_id = ticket_id

    return state
