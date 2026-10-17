"""Entitlement resolution and access-control security boundaries."""

from typing import List, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.db.models import Client, ClientReportEntitlement, Report
from backend.app.core.logging import logger


class EntitlementService:
    """Enforces client report access boundaries independently of LLM reasoning."""

    @staticmethod
    def get_client(client_id: str, db: Session) -> Optional[Client]:
        """Look up client in the database."""
        return db.execute(select(Client).where(Client.id == client_id)).scalar_one_or_none()

    @staticmethod
    def get_authorized_reports(client_id: str, db: Session) -> List[str]:
        """
        Fetch the exact list of report IDs that the client is entitled to access.
        Includes purchased active entitlements PLUS any public excerpt reports.
        The LLM is NEVER the authority for this list.
        """
        # First verify client exists
        client = EntitlementService.get_client(client_id, db)
        if not client:
            logger.warning(f"Unknown client_id '{client_id}' attempted access.")
            return []

        # Purchased reports
        purchased_stmt = select(ClientReportEntitlement.report_id).where(
            ClientReportEntitlement.client_id == client_id,
            ClientReportEntitlement.status == "active"
        )
        purchased_results = db.execute(purchased_stmt).scalars().all()

        # Public excerpt reports available to all registered clients
        public_stmt = select(Report.id).where(Report.access == "public excerpt")
        public_results = db.execute(public_stmt).scalars().all()

        authorized = set(purchased_results).union(set(public_results))
        return sorted(list(authorized))

    @staticmethod
    def is_report_authorized(client_id: str, report_id: str, db: Session) -> bool:
        """Check if client has an active entitlement for a specific report."""
        authorized = EntitlementService.get_authorized_reports(client_id, db)
        return report_id in authorized

    @staticmethod
    def check_catalog_report_exists(report_id: str, db: Session) -> Optional[Report]:
        """Check if report exists in general catalog for upgrade path offers."""
        stmt = select(Report).where(Report.id == report_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def filter_citations(citations: List[dict], client_id: str, db: Session) -> List[dict]:
        """
        Post-retrieval sanity guard: ensure no citation contains an unauthorized report.
        Redacts or removes unauthorized citations completely.
        """
        authorized_set = set(EntitlementService.get_authorized_reports(client_id, db))
        safe_citations = []
        for cit in citations:
            rep_id = cit.get("report_id")
            if rep_id in authorized_set:
                safe_citations.append(cit)
            else:
                logger.error(
                    f"CRITICAL: Leaked citation attempt for report {rep_id} to client {client_id} blocked."
                )
        return safe_citations
