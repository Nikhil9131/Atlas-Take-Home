"""Database session management with multi-dialect support and seed initialization."""

import os
import json
from datetime import date, datetime
from typing import Generator
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.models import (
    Base,
    Report,
    Client,
    ClientReportEntitlement,
    MarketMetric
)


def create_db_engine():
    """Create primary database engine with fallback to SQLite for local development/testing."""
    db_url = settings.DATABASE_URL
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3} if "mysql" in db_url else {}
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected successfully to primary database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to configured database ({e}). Falling back to local SQLite database.")
        sqlite_url = "sqlite:///atlas_local.db"
        fallback_engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False}
        )
        return fallback_engine


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency providing a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database_if_empty(db: Session = None):
    """Seed initial reports, clients, entitlements, and market metrics if empty."""
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        # Create all tables first
        Base.metadata.create_all(bind=engine)

        # Check if already seeded
        existing_report = db.execute(select(Report).limit(1)).scalar_one_or_none()
        if existing_report:
            logger.info("Database already contains seed data.")
            return

        logger.info("Database is empty. Seeding initial assignment data...")

        # 1. Reports
        reports_data = [
            Report(
                id="R-101",
                title="Global Smart Water Meter Market 2025",
                publisher="CMR",
                published=date(2025, 3, 10),
                sector="Utilities",
                access="paid",
                summary="Comprehensive global analysis of smart water metering solutions covering AMR/AMI hardware, analytics software, and field deployment services.",
                metadata_json={"pages": 42, "focus": "Hardware, software, and services", "forecast_years": "2025-2030"}
            ),
            Report(
                id="R-102",
                title="Smart Water Metering: Industry Outlook 2024",
                publisher="Aquila Insights (third party)",
                published=date(2024, 6, 18),
                sector="Utilities",
                access="public excerpt",
                summary="Third-party benchmarking report dedicated strictly to residential and commercial AMR/AMI metering hardware shipments.",
                metadata_json={"pages": 28, "focus": "AMR/AMI hardware only", "forecast_years": "2024-2029"}
            ),
            Report(
                id="R-103",
                title="Residential Water Purifier Market 2025",
                publisher="CMR",
                published=date(2025, 1, 22),
                sector="Consumer Durables",
                access="paid",
                summary="Market assessment for household water purification technologies across POU reverse osmosis, UV filtration, and gravity units.",
                metadata_json={"pages": 36, "focus": "Point-of-use residential purification systems", "forecast_years": "2025-2030"}
            ),
            Report(
                id="R-104",
                title="Commercial EV Fleet Charging Infrastructure 2025",
                publisher="CMR",
                published=date(2025, 2, 14),
                sector="Automotive & Energy",
                access="paid",
                summary="Strategic outlook for commercial fleet electrification and depot megawatt charging stations.",
                metadata_json={"pages": 50, "focus": "Fleet charging depots and high-power DC infrastructure", "forecast_years": "2025-2030"}
            ),
            Report(
                id="R-105",
                title="AI-Powered Diagnostic Imaging Market 2024",
                publisher="MedTech Analytics",
                published=date(2024, 11, 5),
                sector="Healthcare",
                access="paid",
                summary="Clinical AI applications in radiology, MRI, CT scanning, and automated lesion detection.",
                metadata_json={"pages": 34, "focus": "Radiology and diagnostic computer vision software", "forecast_years": "2024-2029"}
            ),
            Report(
                id="R-106",
                title="Cloud-Native Data Security Market 2025",
                publisher="CyberShield Research",
                published=date(2025, 4, 2),
                sector="Cybersecurity & Cloud",
                access="paid",
                summary="Data security posture management (DSPM), multi-cloud tokenization, and confidential computing systems.",
                metadata_json={"pages": 46, "focus": "Enterprise cloud data discovery and protection", "forecast_years": "2025-2030"}
            )
        ]
        db.add_all(reports_data)

        # 2. Clients
        clients_data = [
            Client(id="C-01", company="Northwind Utilities", contact_email="ops@example.com"),
            Client(id="C-02", company="Blue Delta Infra", contact_email="procurement@example.com")
        ]
        db.add_all(clients_data)

        # 3. Entitlements
        entitlements_data = [
            ClientReportEntitlement(client_id="C-01", report_id="R-101", status="active"),
            ClientReportEntitlement(client_id="C-01", report_id="R-103", status="active"),
            ClientReportEntitlement(client_id="C-02", report_id="R-103", status="active")
        ]
        db.add_all(entitlements_data)

        # 4. Market Metrics
        metrics_data = [
            # R-101 Metrics
            MarketMetric(report_id="R-101", metric="Market size", region="Global", year_period="2024", value_text="USD 4.21 B", numeric_value=4.21, unit="USD Billion", scope_note="Includes hardware, software and services", source_page=8),
            MarketMetric(report_id="R-101", metric="CAGR", region="Global", year_period="2025-2030", value_text="11.2 %", numeric_value=11.2, unit="%", scope_note="Forecast period stated as 2025-2030", source_page=8),
            MarketMetric(report_id="R-101", metric="Regional share", region="APAC", year_period="2024", value_text="38 %", numeric_value=38.0, unit="%", scope_note="Share of global market size", source_page=8),

            # R-102 Metrics
            MarketMetric(report_id="R-102", metric="Market size", region="Global", year_period="2024", value_text="USD 3.87 B", numeric_value=3.87, unit="USD Billion", scope_note="AMR / AMI hardware only", source_page=14),
            MarketMetric(report_id="R-102", metric="CAGR", region="Global", year_period="2024-2029", value_text="9.8 %", numeric_value=9.8, unit="%", scope_note="Different forecast window from R-101", source_page=14),
            MarketMetric(report_id="R-102", metric="Regional share", region="APAC", year_period="2024", value_text="41 %", numeric_value=41.0, unit="%", scope_note="Share of hardware market", source_page=14),

            # R-103 Metrics
            MarketMetric(report_id="R-103", metric="Market size", region="Global", year_period="2024", value_text="USD 9.55 B", numeric_value=9.55, unit="USD Billion", scope_note="Includes RO, UV, and Gravity residential purifiers", source_page=6),
            MarketMetric(report_id="R-103", metric="CAGR", region="Global", year_period="2025-2030", value_text="7.8 %", numeric_value=7.8, unit="%", scope_note="Forecast period 2025-2030", source_page=6),
            MarketMetric(report_id="R-103", metric="Regional share", region="APAC", year_period="2024", value_text="52 %", numeric_value=52.0, unit="%", scope_note="Share of global water purifier market", source_page=7),

            # R-104 Metrics
            MarketMetric(report_id="R-104", metric="Market size", region="Global", year_period="2024", value_text="USD 5.10 B", numeric_value=5.10, unit="USD Billion", scope_note="Commercial fleet charging stations and depot software", source_page=10),
            MarketMetric(report_id="R-104", metric="CAGR", region="Global", year_period="2025-2030", value_text="18.5 %", numeric_value=18.5, unit="%", scope_note="Commercial fleet electrification forecast 2025-2030", source_page=10),

            # R-105 Metrics
            MarketMetric(report_id="R-105", metric="Market size", region="Global", year_period="2024", value_text="USD 2.45 B", numeric_value=2.45, unit="USD Billion", scope_note="Radiology AI, automated detection, and oncology imaging", source_page=12),
            MarketMetric(report_id="R-105", metric="CAGR", region="Global", year_period="2024-2029", value_text="24.1 %", numeric_value=24.1, unit="%", scope_note="Clinical adoption window 2024-2029", source_page=12),

            # R-106 Metrics
            MarketMetric(report_id="R-106", metric="Market size", region="Global", year_period="2024", value_text="USD 3.60 B", numeric_value=3.60, unit="USD Billion", scope_note="DSPM, cloud data discovery, tokenization, and encryption", source_page=9),
            MarketMetric(report_id="R-106", metric="CAGR", region="Global", year_period="2025-2030", value_text="16.2 %", numeric_value=16.2, unit="%", scope_note="Enterprise cloud security forecast 2025-2030", source_page=9),
        ]
        db.add_all(metrics_data)
        db.commit()
        logger.info("Database successfully seeded with reports, clients, entitlements, and market metrics.")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed database: {e}")
        raise
    finally:
        if close_after:
            db.close()
