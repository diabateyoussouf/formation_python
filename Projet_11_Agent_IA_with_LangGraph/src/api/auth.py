from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.core.security import hash_password, verify_password, create_access_token
from src.api.deps import get_db, get_current_user
from src.db.models import UserModel

router = APIRouter(prefix="/api/v1/auth", tags=["Authentification"])


# DTOs (Data Transfer Objects) Pydantic
class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    nom_complet: str
    role: str = "client"  # Présent pour la tolérance de validation, mais ignoré en création


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserResponseSchema(BaseModel):
    id: int
    email: str
    nom_complet: str
    role: str

    class Config:
        from_attributes = True  # Permet à Pydantic d'extraire les données directement depuis le modèle SQLAlchemy


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreateSchema, db: Session = Depends(get_db)):
    """Création d'un nouveau compte utilisateur (sécurité : rôle 'client' forcé côté serveur)."""
    existing_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà."
        )

    # Le rôle est obligatoirement 'client', peu importe ce qui est envoyé par le client HTTP
    new_user = UserModel(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        nom_complet=user_in.nom_complet,
        role="client"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenSchema)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authentification et émission du jeton JWT (durée de validité : 7 jours)."""
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Émission d'un jeton valide 7 jours pour maintenir la session Streamlit au F5
    access_token = create_access_token(
        subject=str(user.id), 
        role=user.role, 
        expires_delta=timedelta(days=7)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }


@router.get("/me", response_model=UserResponseSchema)
def get_me(current_user: UserModel = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur connecté (utilisé pour ré-authentifier la session Streamlit)."""
    return current_user