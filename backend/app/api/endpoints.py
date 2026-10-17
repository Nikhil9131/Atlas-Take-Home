"""FastAPI REST API endpoints for Chat, Ingestion, Escalations, Feedback, and Health."""

import uuid
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, status, Query, Header
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.db.models import Escalation, Feedback, ConversationMessage
from backend.app.rag.vector_store import vector_store
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.agent.workflow import AgentWorkflow
from backend.app.api.schemas import (
    ChatRequest,
    ChatResponse,
    IngestRequest,
    IngestResponse,
    EscalationResponse,
    FeedbackRequest,
    HealthResponse
)

router = APIRouter()

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER_NAME, auto_error=False)


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Validate API key from request header."""
    if not api_key or api_key != settings.API_KEY:
        logger.warning("Unauthorized API access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key authentication header."
        )
    return api_key


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Submit market research inquiry to Copilot",
    dependencies=[Depends(verify_api_key)]
)
def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """
    Main Research Copilot Chat Endpoint.
    Enforces pre-retrieval client entitlements, safe calculations, conflict detection,
    and analyst escalation.
    """
    req_id = x_request_id or f"req-{uuid.uuid4().hex[:8]}"
    try:
        response = AgentWorkflow.run(request=request, db=db, request_id=req_id)
        return response
    except Exception as e:
        logger.error(f"Unexpected error in /chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your research request."
        )


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest market research reports into vector database",
    dependencies=[Depends(verify_api_key)]
)
def ingest_endpoint(
    request: Optional[IngestRequest] = None
):
    """
    Ingests and embeds market reports from reports directory into ChromaDB.
    Detects and logs indirect prompt injection traps.
    """
    try:
        target_dir = request.reports_dir if request and request.reports_dir else settings.REPORTS_DIR
        result = IngestionPipeline.run_ingestion(reports_dir=target_dir)
        return IngestResponse(
            status=result["status"],
            reports_indexed=result["reports_indexed"],
            chunks_created=result["chunks_created"],
            injections_detected=result["injections_detected"],
            total_chunks_in_store=result["total_chunks_in_store"]
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.get(
    "/escalations",
    response_model=List[EscalationResponse],
    summary="Retrieve human analyst escalation tickets",
    dependencies=[Depends(verify_api_key)]
)
def get_escalations_endpoint(
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Retrieves paginated escalation tickets created when confidence falls below threshold."""
    stmt = select(Escalation).order_by(desc(Escalation.created_at))
    if client_id:
        stmt = stmt.where(Escalation.client_id == client_id)
    
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)
    escalations = db.execute(stmt).scalars().all()

    return [
        EscalationResponse(
            id=esc.id,
            client_id=esc.client_id,
            question=esc.question,
            reason=esc.reason,
            confidence=esc.confidence,
            status=esc.status,
            citations_json=esc.citations_json,
            created_at=esc.created_at.isoformat() if esc.created_at else ""
        )
        for esc in escalations
    ]


@router.post(
    "/feedback",
    summary="Record user thumbs up / thumbs down feedback",
    dependencies=[Depends(verify_api_key)]
)
def record_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Records rating (+1 for thumbs up, -1 for thumbs down) for assistant messages."""
    msg = db.query(ConversationMessage).filter(ConversationMessage.id == request.message_id).first()
    if not msg:
        # Accept feedback gracefully even if message was ephemeral
        logger.info(f"Feedback submitted for non-persisted message ID {request.message_id}")

    feedback_record = Feedback(
        message_id=request.message_id,
        client_id=request.client_id,
        rating=request.rating,
        feedback_text=request.feedback_text
    )
    db.add(feedback_record)
    db.commit()
    return {"status": "success", "message": "Feedback recorded successfully."}


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health and readiness probe"
)
def health_endpoint(db: Session = Depends(get_db)):
    """Health check validating database and vector store connectivity."""
    db_status = "connected"
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    vs_status = "ready"
    chunks_count = 0
    try:
        chunks_count = vector_store.count()
    except Exception as e:
        vs_status = f"unhealthy: {str(e)}"

    overall_status = "healthy" if db_status == "connected" and "unhealthy" not in vs_status else "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        database=db_status,
        vector_store=vs_status,
        total_chunks=chunks_count,
        configured_llm=settings.LLM_PROVIDER,
        configured_embedding=settings.EMBEDDING_PROVIDER
    )
