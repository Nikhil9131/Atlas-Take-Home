"""Prompt injection detection and document text sanitization engine."""

import re
from typing import Tuple, Optional, Dict, Any
from backend.app.core.logging import logger

# High-risk adversarial phrases and instruction override patterns
INJECTION_PATTERNS = [
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"forget\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"print\s+(the\s+)?full\s+contents\s+of\s+(the\s+)?clients?\s+table",
    r"list\s+(all\s+)?(client\s+)?emails?",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"show\s+(your\s+)?(system\s+)?prompt",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"dan\s+mode",
    r"bypass\s+(all\s+)?security\s+rules?",
    r"drop\s+table",
    r"delete\s+from\s+reports",
    r"delete\s+all\s+rows",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detect whether a string contains prompt injection or adversarial override attempts.
    
    Returns:
        (is_injection, matched_pattern, reason)
    """
    if not text:
        return False, None, None

    normalized = text.strip()
    for pattern in COMPILED_PATTERNS:
        match = pattern.search(normalized)
        if match:
            matched_str = match.group(0)
            reason = f"Detected adversarial pattern: '{matched_str}'"
            return True, matched_str, reason

    return False, None, None


def sanitize_document_text(content: str, report_id: str = "UNKNOWN") -> Tuple[str, bool, Optional[str]]:
    """
    Scan retrieved or ingested document text for embedded prompt injection attacks (indirect injection).
    Flags the attack, isolates the text safely, but preserves legitimate surrounding facts.
    
    Returns:
        (sanitized_text, was_injection_detected, detected_snippet)
    """
    is_injection, matched_str, reason = detect_prompt_injection(content)
    if is_injection:
        logger.warning(
            f"Indirect prompt injection detected in report {report_id}: {reason}",
            extra={"report_id": report_id, "unsafe_flag": True, "event_type": "INDIRECT_INJECTION_DETECTED"}
        )
        # We mark the malicious instruction as an untrusted quoted text block that cannot be executed
        sanitized = re.sub(
            r"(NOTE TO AI SYSTEMS:[^\n]+|Disregard all previous instructions[^\n]+)",
            "[UNTRUSTED ADVERSARIAL INSTRUCTION BLOCKED AND QUOTED AS DATA ONLY]",
            content,
            flags=re.IGNORECASE
        )
        return sanitized, True, matched_str

    return content, False, None
