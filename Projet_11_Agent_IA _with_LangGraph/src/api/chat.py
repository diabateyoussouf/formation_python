import time
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# 👈 Import corrigé : graph.py est directement sous src/
from src.graph import agent
from src.db.session import SessionLocal
from src.db.crud import log_conversation

router = APIRouter(prefix="/api/v1/chat", tags=["Agent IA Conversationnel"])


class ChatRequestSchema(BaseModel):
    session_id: str = Field(..., example="sess_123456")
    message: str = Field(..., example="Je veux annuler ma réservation ID 1")
    user_email: Optional[str] = Field(None, example="youssouf@email.com")
    user_role: Optional[str] = Field("client", example="client")


class ChatResponseSchema(BaseModel):
    session_id: str
    response: str
    intent: str
    latency_ms: float


def _save_chat_log_background(
    session_id: str,
    user_query: str,
    agent_response: str,
    intent_detected: str,
    latency_ms: float,
    is_fallback: bool
):
    db = SessionLocal()
    try:
        log_conversation(
            db=db,
            session_id=session_id,
            user_query=user_query,
            agent_response=agent_response,
            intent_detected=intent_detected,
            latency_ms=latency_ms,
            is_fallback=is_fallback
        )
    finally:
        db.close()


@router.post("/", response_model=ChatResponseSchema)
def chat_with_agent(payload: ChatRequestSchema, background_tasks: BackgroundTasks):
    """Dialogue avec l'agent LangGraph intégrant la mémoire de session et la journalisation BDD."""
    start_time = time.time()
    try:
        # Transmission de thread_id à LangGraph pour la mémoire de session
        config = {"configurable": {"thread_id": payload.session_id}}

        input_state = {
            "question": payload.message,
            "user_email": payload.user_email,
            "user_role": payload.user_role or "client"
        }

        # Exécution du graphe avec Checkpointer
        result = agent.invoke(input_state, config=config)

        latency_ms = round((time.time() - start_time) * 1000, 2)
        response_text = result.get("reponse", "Aucune réponse n'a pu être générée.")
        intent = result.get("decision", "RAG")

        is_fallback = "je ne sais pas" in response_text.lower() or "contacter la réception" in response_text.lower()

        # Enregistrement asynchrone des logs dans SQLite
        background_tasks.add_task(
            _save_chat_log_background,
            session_id=payload.session_id,
            user_query=payload.message,
            agent_response=response_text,
            intent_detected=intent,
            latency_ms=latency_ms,
            is_fallback=is_fallback
        )

        return ChatResponseSchema(
            session_id=payload.session_id,
            response=response_text,
            intent=intent,
            latency_ms=latency_ms
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur interne de l'Agent IA : {str(e)}"
        )