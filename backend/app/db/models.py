"""SQLAlchemy declarative models for Project Atlas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Numeric,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SqlEnum,
    Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=False)
    published = Column(Date, nullable=False)
    sector = Column(String(100), nullable=False, index=True)
    access = Column(String(50), nullable=False, default="paid", index=True)
    summary = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    metrics = relationship("MarketMetric", back_populates="report", cascade="all, delete-orphan")
    entitlements = relationship("ClientReportEntitlement", back_populates="report", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String(50), primary_key=True)
    company = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)  # CONFIDENTIAL: NEVER EXPOSE TO LLM
    created_at = Column(DateTime, default=datetime.utcnow)

    entitlements = relationship("ClientReportEntitlement", back_populates="client", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="client", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="client", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="client", cascade="all, delete-orphan")


class ClientReportEntitlement(Base):
    __tablename__ = "client_report_entitlements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(50), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id = Column(String(50), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active")
    purchased_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="entitlements")
    report = relationship("Report", back_populates="entitlements")


class MarketMetric(Base):
    __tablename__ = "market_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(50), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    metric = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False, default="Global")
    year_period = Column(String(50), nullable=False, index=True)
    value_text = Column(String(100), nullable=False)
    numeric_value = Column(Numeric(15, 4), nullable=False)
    unit = Column(String(50), nullable=False)
    scope_note = Column(Text, nullable=False)
    source_page = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="metrics")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True)
    client_id = Column(String(50), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="New Research Session")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(String(100), primary_key=True)
    conversation_id = Column(String(100), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    response_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(100), ForeignKey("conversation_messages.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(String(50), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1 for thumbs up, -1 for thumbs down
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("ConversationMessage", back_populates="feedback")
    client = relationship("Client", back_populates="feedback")


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(String(100), primary_key=True)
    client_id = Column(String(50), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    reason = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="open", index=True)
    citations_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="escalations")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False, index=True)
    client_id = Column(String(50), nullable=True, index=True)
    request_id = Column(String(100), nullable=True)
    unsafe_flag = Column(Boolean, nullable=False, default=False, index=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
