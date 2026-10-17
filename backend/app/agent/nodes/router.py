"""Router node: Classifies incoming user questions into explicit analytical intents."""

import re
from typing import Tuple
from backend.app.agent.state import AgentState
from backend.app.security.injection_detector import detect_prompt_injection
from backend.app.core.logging import logger

OUT_OF_SCOPE_KEYWORDS = [
    r"\belection\b",
    r"\bpresident\b",
    r"\bpolitics\b",
    r"\bwho\s+will\s+win\b",
    r"\bfootball\b",
    r"\bcricket\b",
    r"\bweather\b",
    r"\brecipe\b",
    r"\bmovie\b",
    r"\bhoroscope\b"
]
COMPILED_OUT_OF_SCOPE = [re.compile(kw, re.IGNORECASE) for kw in OUT_OF_SCOPE_KEYWORDS]

SQL_AGGREGATE_KEYWORDS = [
    r"how\s+many\s+reports",
    r"which\s+sector\s+has\s+the\s+most",
    r"count\s+(the\s+)?reports",
    r"reports\s+in\s+your\s+library",
    r"library\s+statistics",
    r"total\s+reports",
    r"breakdown\s+by\s+sector"
]
COMPILED_SQL_AGGREGATE = [re.compile(kw, re.IGNORECASE) for kw in SQL_AGGREGATE_KEYWORDS]

CALCULATION_KEYWORDS = [
    r"what\s+will\s+.*be\s+worth\s+in\s+\d{4}",
    r"project(ed|ion)?\s+for\s+\d{4}",
    r"calculate\s+cagr",
    r"cagr\s+projection",
    r"future\s+value",
    r"worth\s+in\s+2030",
    r"worth\s+in\s+2035"
]
COMPILED_CALCULATION = [re.compile(kw, re.IGNORECASE) for kw in CALCULATION_KEYWORDS]

COMPARISON_KEYWORDS = [
    r"which\s+report\s+should\s+i\s+trust",
    r"compare\s+report",
    r"difference\s+between\s+r-",
    r"reconcile\s+reports",
    r"why\s+do\s+these\s+reports\s+differ"
]
COMPILED_COMPARISON = [re.compile(kw, re.IGNORECASE) for kw in COMPARISON_KEYWORDS]


def router_node(state: AgentState) -> AgentState:
    """Classifies user question into validated intent with priority ordering."""
    question = state.question.strip()

    # 1. Check for prompt injection & security attacks first
    is_injection, matched, reason = detect_prompt_injection(question)
    if is_injection:
        state.intent = "unsafe"
        state.intent_reason = reason
        logger.warning(
            f"Question classified as UNSAFE for client {state.client_id}: {reason}",
            extra={"client_id": state.client_id, "unsafe_flag": True, "event_type": "PROMPT_INJECTION_BLOCKED"}
        )
        return state

    # 2. Check for out-of-scope queries
    for pattern in COMPILED_OUT_OF_SCOPE:
        if pattern.search(question):
            state.intent = "out_of_scope"
            state.intent_reason = "Question pertains to non-market research domain."
            logger.info(f"Question classified as OUT_OF_SCOPE: '{question}'")
            return state

    # 3. Check for SQL Aggregate questions
    for pattern in COMPILED_SQL_AGGREGATE:
        if pattern.search(question):
            state.intent = "sql_aggregate"
            state.intent_reason = "Aggregate metadata inquiry over library reports."
            logger.info(f"Question classified as SQL_AGGREGATE: '{question}'")
            return state

    # 4. Check for Calculations / Projections
    for pattern in COMPILED_CALCULATION:
        if pattern.search(question):
            state.intent = "calculation"
            state.intent_reason = "Forward-looking calculation or market projection."
            logger.info(f"Question classified as CALCULATION: '{question}'")
            return state

    # 5. Check for Comparisons
    for pattern in COMPILED_COMPARISON:
        if pattern.search(question):
            state.intent = "comparison"
            state.intent_reason = "Cross-source report comparison or trustworthiness inquiry."
            logger.info(f"Question classified as COMPARISON: '{question}'")
            return state

    # 6. Default to Factual
    state.intent = "factual"
    state.intent_reason = "Standard market factual lookup."
    return state
