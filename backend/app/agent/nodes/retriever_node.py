"""Retriever node: Executes entitlement-filtered vector search and structured metric retrieval."""

import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.agent.state import AgentState
from backend.app.security.entitlements import EntitlementService
from backend.app.rag.vector_store import vector_store
from backend.app.db.models import MarketMetric, Report
from backend.app.core.logging import logger


def retriever_node(state: AgentState, db: Session) -> AgentState:
    """Fetches evidence only from reports authorized for the calling client."""
    # 1. Resolve client identity and entitlements
    client = EntitlementService.get_client(state.client_id, db)
    if not client:
        state.is_client_valid = False
        state.authorized_reports = []
        logger.warning(f"Invalid client_id '{state.client_id}' in retriever.")
        return state

    authorized_reports = EntitlementService.get_authorized_reports(state.client_id, db)
    state.authorized_reports = authorized_reports

    # 2. Check if user is asking about a specific unpurchased report (e.g. R-101 by C-02)
    mentioned_reports = re.findall(r"\b(R-\d{3})\b", state.question, re.IGNORECASE)
    unauthorized_requested = []
    for rep in mentioned_reports:
        rep_upper = rep.upper()
        if rep_upper not in authorized_reports:
            catalog_rep = EntitlementService.check_catalog_report_exists(rep_upper, db)
            if catalog_rep:
                unauthorized_requested.append(catalog_rep)

    if unauthorized_requested:
        # Client asked for a report they don't own
        logger.info(
            f"Client {state.client_id} requested unpurchased report(s): {[r.id for r in unauthorized_requested]}"
        )
        state.critic_notes.append(f"UNPURCHASED_REQUEST:{unauthorized_requested[0].id}:{unauthorized_requested[0].title}")

    # If client has no authorized reports, stop retrieval
    if not authorized_reports:
        state.retrieved_chunks = []
        state.retrieved_metrics = []
        return state

    # 3. Vector retrieval with STRICT pre-retrieval filtering
    chunks = vector_store.query(
        query_text=state.question,
        authorized_report_ids=authorized_reports,
        top_k=5
    )
    state.retrieved_chunks = chunks

    # 4. Fetch structured verified metrics for authorized reports
    stmt = select(MarketMetric).where(MarketMetric.report_id.in_(authorized_reports))
    metrics = db.execute(stmt).scalars().all()
    state.retrieved_metrics = [
        {
            "report_id": m.report_id,
            "metric": m.metric,
            "region": m.region,
            "year_period": m.year_period,
            "value_text": m.value_text,
            "numeric_value": float(m.numeric_value),
            "unit": m.unit,
            "scope_note": m.scope_note,
            "source_page": m.source_page
        }
        for m in metrics
    ]

    return state
