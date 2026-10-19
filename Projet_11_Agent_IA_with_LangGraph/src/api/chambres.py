from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_admin
from src.db.models import ChambreModel, UserModel

router = APIRouter(prefix="/api/v1/chambres", tags=["Gestion des Chambres"])


# --- DTOs / SCHÉMAS PYDANTIC ---

class ChambreCreateSchema(BaseModel):
    nom: str = Field(..., example="Suite Royale Vue Jardin")
    surface: str = Field(..., example="45 m²")
    vue: str = Field(..., example="Vue sur le jardin impérial")
    lit: str = Field(..., example="Lit King Size VIP")
    prix_basse: float = Field(..., example=180.0)
    prix_haute: float = Field(..., example=230.0)
    stock: int = Field(..., example=3)
    image_url: str = Field(..., example="https://images.unsplash.com/photo-1611892440504-42a792e24d32")
    equipements: str = Field(..., example="Wi-Fi Fibre, Jacuzzi, Mini-bar")


class ChambreUpdateSchema(BaseModel):
    nom: Optional[str] = None
    surface: Optional[str] = None
    vue: Optional[str] = None
    lit: Optional[str] = None
    prix_basse: Optional[float] = None
    prix_haute: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    equipements: Optional[str] = None


class ChambreResponseSchema(ChambreCreateSchema):
    id: int

    class Config:
        from_attributes = True


# --- ROUTES PUBLIQUES (LECTURE) ---

@router.get("/", response_model=List[ChambreResponseSchema])
def list_chambres(db: Session = Depends(get_db)):
    """Consultation publique du catalogue complet des chambres."""
    return db.query(ChambreModel).all()


@router.get("/{chambre_id}", response_model=ChambreResponseSchema)
def get_chambre(chambre_id: int, db: Session = Depends(get_db)):
    """Détail d'une chambre par son ID."""
    chambre = db.query(ChambreModel).filter(ChambreModel.id == chambre_id).first()
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre introuvable.")
    return chambre


# --- ROUTES ADMINISTRATEUR (ÉCRITURE / MODIFICATION / SUPPRESSION) ---

@router.post("/", response_model=ChambreResponseSchema, status_code=status.HTTP_201_CREATED)
def create_chambre(
    chambre_in: ChambreCreateSchema,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(get_current_admin)
):
    """Ajout d'une nouvelle chambre dans la BDD (RÉSERVÉ ADMIN)."""
    existing = db.query(ChambreModel).filter(ChambreModel.nom == chambre_in.nom).first()
    if existing:
        raise HTTPException(status_code=400, detail="Une chambre portant ce nom existe déjà.")

    new_chambre = ChambreModel(**chambre_in.model_dump())
    db.add(new_chambre)
    db.commit()
    db.refresh(new_chambre)
    return new_chambre


@router.put("/{chambre_id}", response_model=ChambreResponseSchema)
def update_chambre(
    chambre_id: int,
    chambre_in: ChambreUpdateSchema,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(get_current_admin)
):
    """Mise à jour complète ou partielle d'une chambre (RÉSERVÉ ADMIN)."""
    chambre = db.query(ChambreModel).filter(ChambreModel.id == chambre_id).first()
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre introuvable.")

    # Validation de l'unicité du nom en cas de modification
    if chambre_in.nom and chambre_in.nom != chambre.nom:
        existing = db.query(ChambreModel).filter(ChambreModel.nom == chambre_in.nom).first()
        if existing:
            raise HTTPException(status_code=400, detail="Une chambre portant ce nom existe déjà.")

    # Mise à jour dynamique des champs renseignés
    update_data = chambre_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chambre, field, value)

    db.commit()
    db.refresh(chambre)
    return chambre


@router.delete("/{chambre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chambre(
    chambre_id: int,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(get_current_admin)
):
    """Suppression définitive d'une chambre du catalogue (RÉSERVÉ ADMIN)."""
    chambre = db.query(ChambreModel).filter(ChambreModel.id == chambre_id).first()
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre introuvable.")

    db.delete(chambre)
    db.commit()
    return None