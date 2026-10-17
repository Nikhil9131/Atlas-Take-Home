"""Agent Workflow Engine orchestrating Router, Retriever, Calculator, Conflict, Critic, and Escalator nodes."""

import uuid
import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.api.schemas import ChatRequest, ChatResponse
from backend.app.agent.state import AgentState
from backend.app.agent.nodes.router import router_node
from backend.app.agent.nodes.retriever_node import retriever_node
from backend.app.agent.nodes.calculator_node import calculator_node
from backend.app.agent.nodes.conflict_node import conflict_node
from backend.app.agent.nodes.critic_node import critic_node
from backend.app.agent.nodes.escalation_node import escalation_node
from backend.app.agent.nodes.writer_node import writer_node
from backend.app.db.models import Conversation, ConversationMessage, AuditEvent
from backend.app.core.logging import logger


class AgentWorkflow:
    """Orchestrates research copilot pipeline adhering strictly to security and entitlement boundaries."""

    @staticmethod
    def run(request: ChatRequest, db: Session, request_id: Optional[str] = None) -> ChatResponse:
        req_id = request_id or f"req-{uuid.uuid4().hex[:8]}"
        conv_id = request.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        # Initialize State
        state = AgentState(
            client_id=request.client_id,
            question=request.question,
            request_id=req_id,
            conversation_id=conv_id
        )

        logger.info(
            f"Starting agent workflow for client {request.client_id} (req: {req_id}): '{request.question[:60]}...'",
            extra={"client_id": request.client_id, "request_id": req_id}
        )

        # Ensure conversation exists in DB
        existing_conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if not existing_conv:
            new_conv = Conversation(
                id=conv_id,
                client_id=request.client_id,
                title=request.question[:40] + "..." if len(request.question) > 40 else request.question
            )
            try:
                db.add(new_conv)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.warning(f"Could not persist new conversation: {e}")

        # Record User Message
        user_msg_id = f"msg-{uuid.uuid4().hex[:8]}"
        user_msg = ConversationMessage(
            id=user_msg_id,
            conversation_id=conv_id,
            role="user",
            content=request.question,
            response_metadata=None
        )
        try:
            db.add(user_msg)
            db.commit()
        except Exception as e:
            db.rollback()

        # Step 1: Router Node (Intent & Safety Classification)
        state = router_node(state)

        # Fast-path for unsafe / prompt injection attacks
        if state.intent == "unsafe":
            state = writer_node(state, db)
            state.confidence = 1.0
            return AgentWorkflow._finalize_response(state, db, conv_id, start_time)

        # Fast-path for out of scope
        if state.intent == "out_of_scope":
            state = writer_node(state, db)
            state.confidence = 1.0
            return AgentWorkflow._finalize_response(state, db, conv_id, start_time)

        # Step 2: Retriever Node (Entitlement-aware vector + SQL metrics)
        state = retriever_node(state, db)

        # Step 3: Calculator Node (CAGR / derived estimates)
        if state.intent == "calculation" or any(w in state.question.lower() for w in ["cagr", "2030", "2035", "project"]):
            state = calculator_node(state)

        # Step 4: Conflict Node (Scope difference detection)
        state = conflict_node(state)

        # Step 5: Critic Node (Evidence verification & confidence calibration)
        state = critic_node(state, db)

        # Step 6: Escalation Node (Persist ticket in MySQL if confidence < threshold or conflict)
        if state.escalated:
            state = escalation_node(state, db)

        # Step 7: Writer Node (Ground response adhering to facts)
        state = writer_node(state, db)

        return AgentWorkflow._finalize_response(state, db, conv_id, start_time)

    @staticmethod
    def _finalize_response(
        state: AgentState,
        db: Session,
        conv_id: str,
        start_time: float
    ) -> ChatResponse:
        duration_ms = (time.time() - start_time) * 1000.0

        # Persist Assistant Response Message
        asst_msg_id = f"msg-{uuid.uuid4().hex[:8]}"
        metadata = {
            "confidence": state.confidence,
            "escalated": state.escalated,
            "ticket_id": state.ticket_id,
            "citations_count": len(state.citations),
            "conflicts_count": len(state.conflicts),
            "duration_ms": round(duration_ms, 2)
        }
        asst_msg = ConversationMessage(
            id=asst_msg_id,
            conversation_id=conv_id,
            role="assistant",
            content=state.answer,
            response_metadata=metadata
        )
        try:
            db.add(asst_msg)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Could not persist assistant message: {e}")

        logger.info(
            f"Completed workflow in {duration_ms:.2f}ms. Escalated: {state.escalated}, Confidence: {state.confidence:.2f}",
            extra={"duration_ms": duration_ms, "client_id": state.client_id, "request_id": state.request_id}
        )

        return ChatResponse(
            answer=state.answer,
            citations=state.citations,
            confidence=round(state.confidence, 2),
            conflicts=state.conflicts,
            derived_values=state.derived_values,
            escalated=state.escalated,
            ticket_id=state.ticket_id,
            request_id=state.request_id,
            conversation_id=conv_id
        )
