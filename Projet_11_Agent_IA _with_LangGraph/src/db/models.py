from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ============================================================
# 0. CLASSE DE BASE DECLARATIVE
# ============================================================
class Base(DeclarativeBase):
    pass


# ============================================================
# 1. TABLE MÉTIER : Chambres
# ============================================================
class ChambreModel(Base):
    __tablename__ = "chambres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    surface: Mapped[str] = mapped_column(String(50))
    vue: Mapped[str] = mapped_column(String(100))
    lit: Mapped[str] = mapped_column(String(100))
    prix_basse: Mapped[float] = mapped_column(Float, nullable=False)
    prix_haute: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str] = mapped_column(Text)
    equipements: Mapped[str] = mapped_column(Text)

    reservations: Mapped[List["ReservationModel"]] = relationship(back_populates="chambre")


# ============================================================
# 2. TABLE MÉTIER : Réservations (Mise à jour avec Garanties & Statuts)
# ============================================================
class ReservationModel(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_client: Mapped[str] = mapped_column(String(100), nullable=False)
    email_client: Mapped[str] = mapped_column(String(100), nullable=False)
    chambre_id: Mapped[int] = mapped_column(ForeignKey("chambres.id"), nullable=False)
    date_arrivee: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_depart: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    nb_personnes: Mapped[int] = mapped_column(Integer, default=1)
    prix_total: Mapped[float] = mapped_column(Float, nullable=False)
    
    # NOUVEAUX CHAMPS AJOUTÉS
    statut: Mapped[str] = mapped_column(String(50), default="EN_ATTENTE")  # "EN_ATTENTE", "CONFIRMEE", "ANNULEE", "EXPIREE"
    mode_garantie: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "RECEPTION", "VIREMENT", "CARTE"
    ref_virement: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Optionnel pour virement
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chambre: Mapped["ChambreModel"] = relationship(back_populates="reservations")


# ============================================================
# 3. TABLE TÉLÉMÉTRIE : Audit & LLMOps Logs
# ============================================================
class ConversationLogModel(Base):
    __tablename__ = "conversation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(50), index=True)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    agent_response: Mapped[str] = mapped_column(Text, nullable=False)
    intent_detected: Mapped[Optional[str]] = mapped_column(String(20))
    latency_ms: Mapped[Optional[float]] = mapped_column(Float)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    guardrail_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    guardrail_reason: Mapped[Optional[str]] = mapped_column(String(255))
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============================================================
# 4. TABLE SÉCURITÉ : Utilisateurs & Authentification JWT
# ============================================================
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    nom_complet: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="client")  # "client" ou "admin"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)