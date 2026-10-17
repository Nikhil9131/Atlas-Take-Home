"""Critic and fact-checker node: Verifies evidence provenance and calibrates confidence."""

from sqlalchemy.orm import Session
from backend.app.agent.state import AgentState
from backend.app.security.entitlements import EntitlementService
from backend.app.core.config import settings
from backend.app.core.logging import logger


def critic_node(state: AgentState, db: Session) -> AgentState:
    """Verifies that all citations are strictly entitled and computes a calibrated confidence score."""
    # 1. Post-retrieval citation security check: eliminate any unauthorized citation
    if state.citations:
        safe_cits = []
        for cit in state.citations:
            if cit.report_id in state.authorized_reports:
                safe_cits.append(cit)
            else:
                logger.error(
                    f"Critic blocked unauthorized citation {cit.report_id} for client {state.client_id}"
                )
        state.citations = safe_cits

    # 2. Check for empty evidence on factual market research questions
    if state.intent in ("factual", "comparison", "calculation"):
        has_citations = len(state.citations) > 0
        has_derived = len(state.derived_values) > 0
        has_chunks = len(state.retrieved_chunks) > 0

        # Check if query was an unpurchased report inquiry (e.g. C-02 asking for R-101)
        is_unpurchased_request = any(note.startswith("UNPURCHASED_REQUEST:") for note in state.critic_notes)
        if is_unpurchased_request:
            state.confidence = 1.0
            return state

        # Check evidence relevance
        has_relevant_chunks = False
        if state.retrieved_chunks:
            top_score = state.retrieved_chunks[0].get("score", 0.0)
            q_words = {w.lower() for w in state.question.split() if len(w) > 4 and w.lower() not in {"what", "which", "where", "about", "market", "global", "projected", "revenue"}}
            content_words = state.retrieved_chunks[0]["content"].lower()
            keyword_overlap = any(w in content_words for w in q_words)
            if top_score >= 0.55 or keyword_overlap:
                has_relevant_chunks = True

        if not has_citations and not has_derived and not has_relevant_chunks:
            # Insufficient relevant evidence found in entitled library
            state.confidence = 0.35
            state.escalated = True
            state.escalation_reason = (
                "Insufficient evidence in currently entitled reports to substantiate a verified answer. "
                "Automatic escalation initiated to prevent unsubstantiated claims."
            )
            state.critic_notes.append("INSUFFICIENT_EVIDENCE")
            logger.info("Critic escalated due to zero or low-relevance retrieved evidence.")
            return state

    # 3. If already flagged for escalation by earlier nodes (e.g. 2035 window)
    if state.escalated:
        if state.confidence >= settings.ESCALATION_CONFIDENCE_THRESHOLD:
            state.confidence = 0.50
        return state

    # 4. Standard calibrated scoring
    if state.intent in ("unsafe", "out_of_scope"):
        state.confidence = 1.0
    elif state.derived_values:
        state.confidence = 0.85
    elif state.conflicts:
        state.confidence = 0.88
    elif state.citations:
        state.confidence = 0.95
    else:
        state.confidence = 0.75

    # Check against escalation threshold
    if state.confidence < settings.ESCALATION_CONFIDENCE_THRESHOLD:
        state.escalated = True
        state.escalation_reason = (
            f"Confidence score ({state.confidence:.2f}) fell below required threshold "
            f"({settings.ESCALATION_CONFIDENCE_THRESHOLD:.2f})."
        )

    return state
