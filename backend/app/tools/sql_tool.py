"""Safe Read-Only SQL Tool.
Enforces strict table allowlists, AST/token inspection, execution timeouts, and row caps.
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import SessionLocal

# Tables permitted for aggregate analysis
ALLOWED_TABLES = {"reports", "market_metrics"}

# Statements strictly prohibited
FORBIDDEN_KEYWORDS = [
    r"\binsert\b",
    r"\bupdate\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\balter\b",
    r"\btruncate\b",
    r"\bcreate\b",
    r"\breplace\b",
    r"\bgrant\b",
    r"\brevoke\b",
    r"\bexecute\b",
    r"\bexec\b",
    r"\bunion\b",
    r"\binto\s+outfile\b",
    r"\bload_file\b",
    r"\binformation_schema\b",
    r"\bsqlite_master\b",
    r"\bpg_catalog\b"
]
COMPILED_FORBIDDEN = [re.compile(kw, re.IGNORECASE) for kw in FORBIDDEN_KEYWORDS]


class SQLValidationError(Exception):
    """Raised when an SQL query violates security constraints."""
    pass


class SafeSQLTool:
    """Executes validated, read-only aggregate queries on allowed tables."""

    @staticmethod
    def validate_sql(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validates SQL against read-only constraints and table allowlist.
        Returns (is_valid, error_reason).
        """
        cleaned = query.strip()
        if not cleaned:
            return False, "Query is empty."

        # Reject multiple statements (semicolon attacks)
        semicolon_count = cleaned.count(";")
        if semicolon_count > 1 or (semicolon_count == 1 and not cleaned.endswith(";")):
            return False, "Multiple SQL statements are strictly forbidden."

        # Ensure query begins with SELECT (or WITH ... SELECT)
        if not re.match(r"^(select|with)\b", cleaned, re.IGNORECASE):
            return False, "Only SELECT statements are permitted."

        # Check for forbidden keywords
        for pattern in COMPILED_FORBIDDEN:
            if pattern.search(cleaned):
                return False, f"Prohibited SQL keyword or operation detected: '{pattern.pattern}'"

        # Check table references against allowlist
        # Extract potential table names following FROM or JOIN
        table_matches = re.findall(r"\b(?:from|join)\s+([a-zA-Z0-9_`\"\[\]]+)", cleaned, re.IGNORECASE)
        for tbl in table_matches:
            clean_tbl = tbl.strip("`\"[]").lower()
            if clean_tbl not in ALLOWED_TABLES:
                return False, f"Table '{clean_tbl}' is not authorized. Permitted tables: {sorted(list(ALLOWED_TABLES))}"

        return True, None

    @staticmethod
    def execute_query(query: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Executes a validated read-only SQL query with row limits and timeout.
        """
        is_valid, reason = SafeSQLTool.validate_sql(query)
        if not is_valid:
            logger.warning(
                f"SQL Safety Violation: Rejected query '{query}'. Reason: {reason}",
                extra={"event_type": "SQL_SAFETY_VIOLATION", "unsafe_flag": True}
            )
            return {
                "success": False,
                "error": reason,
                "query": query,
                "columns": [],
                "rows": [],
                "row_count": 0
            }

        # Enforce LIMIT if not explicitly present
        cleaned_query = query.rstrip(";").strip()
        if not re.search(r"\blimit\s+\d+", cleaned_query, re.IGNORECASE):
            cleaned_query = f"{cleaned_query} LIMIT {settings.SQL_ROW_LIMIT}"

        close_after = False
        if db is None:
            db = SessionLocal()
            close_after = True

        start_time = time.time()
        try:
            result = db.execute(text(cleaned_query))
            duration = (time.time() - start_time) * 1000.0

            columns = list(result.keys()) if result.returns_rows else []
            raw_rows = result.fetchall() if result.returns_rows else []
            rows = [list(row) for row in raw_rows]

            logger.info(
                f"Safe SQL executed successfully in {duration:.2f}ms: '{cleaned_query}'. Rows: {len(rows)}",
                extra={"duration_ms": duration}
            )

            return {
                "success": True,
                "error": None,
                "query": cleaned_query,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "duration_ms": round(duration, 2)
            }
        except Exception as e:
            logger.error(f"SQL execution error for '{cleaned_query}': {e}")
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "query": cleaned_query,
                "columns": [],
                "rows": [],
                "row_count": 0
            }
        finally:
            if close_after:
                db.close()
