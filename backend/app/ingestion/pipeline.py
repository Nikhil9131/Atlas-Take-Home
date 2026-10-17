"""Full report ingestion pipeline orchestrating parsing, validation, and vector storage."""

import os
from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.ingestion.chunker import ReportParser, DocumentChunk
from backend.app.rag.vector_store import vector_store


class IngestionPipeline:
    """Orchestrates parsing, metadata extraction, injection checking, and vector indexing."""

    @staticmethod
    def run_ingestion(reports_dir: str = None) -> Dict[str, Any]:
        target_dir = reports_dir or settings.REPORTS_DIR
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Reports directory not found: {target_dir}")

        report_files = [
            os.path.join(target_dir, f)
            for f in os.listdir(target_dir)
            if f.endswith(".md") or f.endswith(".txt")
        ]

        if not report_files:
            logger.warning(f"No report files found in {target_dir}")
            return {
                "status": "warning",
                "message": "No reports found to ingest",
                "reports_indexed": [],
                "chunks_created": 0,
                "injections_detected": 0
            }

        all_chunks: List[DocumentChunk] = []
        indexed_reports: List[str] = []
        injections_detected = 0

        for file_path in report_files:
            try:
                chunks = ReportParser.parse_file(file_path)
                for chunk in chunks:
                    if chunk.is_injection_detected:
                        injections_detected += 1
                all_chunks.extend(chunks)
                indexed_reports.append(os.path.basename(file_path))
            except Exception as e:
                logger.error(f"Failed to parse report {file_path}: {e}")

        # Store in Vector Database
        chunks_stored = vector_store.add_chunks(all_chunks)

        logger.info(
            f"Ingestion completed: {len(indexed_reports)} reports, {chunks_stored} chunks, "
            f"{injections_detected} injections detected."
        )

        return {
            "status": "success",
            "reports_indexed": indexed_reports,
            "chunks_created": chunks_stored,
            "injections_detected": injections_detected,
            "total_chunks_in_store": vector_store.count()
        }
