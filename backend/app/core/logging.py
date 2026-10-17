"""Structured logging configuration for Project Atlas."""

import json
import logging
import sys
import time
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Include custom fields if present
        for field in ("request_id", "client_id", "duration_ms", "tokens_used", "event_type", "unsafe_flag"):
            if hasattr(record, field):
                log_obj[field] = getattr(record, field)
                
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)


def setup_logger(name: str = "atlas") -> logging.Logger:
    """Initialize and return a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = setup_logger()
