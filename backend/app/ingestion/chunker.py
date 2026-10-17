"""Document chunking and metadata extraction for market research reports."""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from backend.app.security.injection_detector import sanitize_document_text
from backend.app.core.logging import logger


@dataclass
class DocumentChunk:
    chunk_id: str
    report_id: str
    report_title: str
    sector: str
    page: int
    access: str
    content: str
    is_injection_detected: bool = False
    injected_snippet: Optional[str] = None


class ReportParser:
    """Parses structured markdown market reports and extracts pages and metadata."""

    @staticmethod
    def parse_file(file_path: str) -> List[DocumentChunk]:
        """Read a markdown report file and produce deterministic DocumentChunks."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Report file not found: {file_path}")

        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Extract Report ID from filename or header (e.g. R-101)
        id_match = re.search(r"R-\d{3}", filename) or re.search(r"R-\d{3}", raw_text)
        report_id = id_match.group(0) if id_match else "R-UNKNOWN"

        # Extract Title
        title_match = re.search(r"^#\s+([^\n]+)", raw_text, re.MULTILINE)
        report_title = title_match.group(1).strip() if title_match else filename

        # Extract Sector
        sector_match = re.search(r"\*\*Sector:\*\*\s*([^\n]+)", raw_text)
        sector = sector_match.group(1).strip() if sector_match else "General"

        # Extract Access
        access_match = re.search(r"\*\*Access Classification:\*\*\s*([^\n]+)", raw_text)
        access = access_match.group(1).strip() if access_match else "paid"

        # Split into pages by <!-- page X -->
        page_pattern = re.compile(r"<!--\s*page\s*(\d+)\s*-->", re.IGNORECASE)
        parts = page_pattern.split(raw_text)

        chunks: List[DocumentChunk] = []
        global_chunk_idx = 1

        # If no page markers, treat entire text as page 1
        if len(parts) == 1:
            page_chunks, global_chunk_idx = ReportParser._chunk_text(
                parts[0], report_id, report_title, sector, 1, access, global_chunk_idx
            )
            chunks.extend(page_chunks)
        else:
            # Header content before first page marker (treat as page 0 or cover metadata)
            header_text = parts[0].strip()
            if header_text:
                page_chunks, global_chunk_idx = ReportParser._chunk_text(
                    header_text, report_id, report_title, sector, 1, access, global_chunk_idx
                )
                chunks.extend(page_chunks)

            # Subsequent parts come in pairs: (page_num_str, page_content)
            for i in range(1, len(parts), 2):
                page_num = int(parts[i])
                page_content = parts[i + 1].strip() if (i + 1) < len(parts) else ""
                if page_content:
                    page_chunks, global_chunk_idx = ReportParser._chunk_text(
                        page_content, report_id, report_title, sector, page_num, access, global_chunk_idx
                    )
                    chunks.extend(page_chunks)

        logger.info(f"Parsed report {report_id} into {len(chunks)} chunks.")
        return chunks

    @staticmethod
    def _chunk_text(
        text: str,
        report_id: str,
        report_title: str,
        sector: str,
        page: int,
        access: str,
        start_idx: int = 1,
        max_chunk_chars: int = 600,
        overlap_chars: int = 100
    ) -> Tuple[List[DocumentChunk], int]:
        """Split text of a single page into overlapping chunks with injection detection."""
        sanitized_text, is_injection, snippet = sanitize_document_text(text, report_id=report_id)
        paragraphs = [p.strip() for p in sanitized_text.split("\n\n") if p.strip()]
        chunks: List[DocumentChunk] = []
        current_chunk = ""
        current_idx = start_idx

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chunk_chars:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    cid = f"{report_id}_p{page}_c{current_idx}"
                    chunks.append(DocumentChunk(
                        chunk_id=cid,
                        report_id=report_id,
                        report_title=report_title,
                        sector=sector,
                        page=page,
                        access=access,
                        content=current_chunk,
                        is_injection_detected=is_injection,
                        injected_snippet=snippet
                    ))
                    current_idx += 1
                current_chunk = para

        if current_chunk:
            cid = f"{report_id}_p{page}_c{current_idx}"
            chunks.append(DocumentChunk(
                chunk_id=cid,
                report_id=report_id,
                report_title=report_title,
                sector=sector,
                page=page,
                access=access,
                content=current_chunk,
                is_injection_detected=is_injection,
                injected_snippet=snippet
            ))
            current_idx += 1

        return chunks, current_idx
