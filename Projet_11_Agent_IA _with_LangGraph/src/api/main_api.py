from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.db.session import init_db
from src.rag import obtenir_retriever  # <-- Préchargement de la base RAG
from src.api.auth import router as auth_router
from src.api.chambres import router as chambres_router
from src.api.reservations import router as reservations_router
from src.api.chat import router as chat_router
from src.api.deps import get_current_user
from src.db.models import UserModel

app = FastAPI(
    title="Hôtel Le Belvédère — Enterprise AI & Auth API",
    version="2.0.0",
    description="API RESTful avec JWT, CRUD Métier et orchestration LangGraph."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    print("🚀 Initialisation de la base de données...")
    init_db()
    print("🚀 Chargement du modèle d'embeddings et de la base RAG en mémoire...")
    obtenir_retriever()
    print("✅ Base RAG prête à répondre !")

# Routeurs API
app.include_router(auth_router)
app.include_router(chambres_router)
app.include_router(reservations_router)
app.include_router(chat_router)


@app.get("/api/v1/protected-test", tags=["Tests Sécurité"])
def protected_route(current_user: UserModel = Depends(get_current_user)):
    return {
        "message": f"Bienvenue {current_user.nom_complet} ! Accès autorisé.",
        "user_id": current_user.id,
        "role": current_user.role
    }