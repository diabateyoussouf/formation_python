from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from src.db.models import ChambreModel, ReservationModel, ConversationLogModel


def log_conversation(
    db: Session,
    session_id: str,
    user_query: str,
    agent_response: str,
    intent_detected: str,
    latency_ms: float,
    is_fallback: bool = False,
    guardrail_flagged: bool = False,
    guardrail_reason: Optional[str] = None
) -> ConversationLogModel:
    """Enregistre la trace d'interaction pour la télémétrie LLMOps."""
    log_entry = ConversationLogModel(
        session_id=session_id,
        user_query=user_query,
        agent_response=agent_response,
        intent_detected=intent_detected,
        latency_ms=latency_ms,
        is_fallback=is_fallback,
        guardrail_flagged=guardrail_flagged,
        guardrail_reason=guardrail_reason
    )
    db.add(log_entry)
    db.commit()
    return log_entry