from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocale
from backend import models
from datetime import date
from backend.routes.auth import get_current_user

fabricant_router = APIRouter(prefix="/fabricant", tags=["Fabricant"])

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

def get_fabricant_id(user=Depends(get_current_user)):
    if user.type_utilisateur != "fabricant":
        raise HTTPException(status_code=403, detail="Accès réservé aux fabricants")
    return user.id

class MedicamentRequest(BaseModel):
    nom: str
    description: str
    date_expiration: date
    quantite: int 

@fabricant_router.get("/infos")
def voir_infos_fabricant(
    db: Session = Depends(get_db),
    fabricant_id: int = Depends(get_fabricant_id)
):
    utilisateur = db.query(models.Utilisateur).get(fabricant_id)
    if not utilisateur or utilisateur.type_utilisateur != "fabricant":
        raise HTTPException(status_code=404, detail="Fabricant non trouvé")
    return utilisateur

@fabricant_router.get("/demandes-medicaments")
def voir_mes_demandes(
    db: Session = Depends(get_db),
    fabricant_id: int = Depends(get_fabricant_id)
):
    return db.query(models.DemandeMedicament).filter_by(id_fabricant=fabricant_id).all()

@fabricant_router.get("/demandes-medicaments/{id}")
def voir_demande_detail(
    id: int,
    db: Session = Depends(get_db),
    fabricant_id: int = Depends(get_fabricant_id)
):
    demande = db.query(models.DemandeMedicament).get(id)
    if not demande or demande.id_fabricant != fabricant_id:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    return demande

# ✅ 4. Soumettre une nouvelle demande de médicament
@fabricant_router.post("/demandes-medicaments")
def soumettre_demande(
    data: MedicamentRequest,
    db: Session = Depends(get_db),
    fabricant_id: int = Depends(get_fabricant_id)
):
    demande = models.DemandeMedicament(
        nom=data.nom,
        description=data.description,
        date_expiration=data.date_expiration,
        quantite=data.quantite, 
        statut="en_attente",
        id_fabricant=fabricant_id
    )
    db.add(demande)
    db.commit()
    db.refresh(demande)
    return {"message": "Demande soumise avec succès", "demande": demande}

@fabricant_router.delete("/demandes-medicaments/{id}")
def supprimer_demande(
    id: int,
    db: Session = Depends(get_db),
    fabricant_id: int = Depends(get_fabricant_id)
):
    demande = db.query(models.DemandeMedicament).get(id)
    if not demande or demande.id_fabricant != fabricant_id:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    if demande.statut != "en_attente":
        raise HTTPException(status_code=400, detail="Impossible de supprimer une demande déjà traitée")

    db.delete(demande)
    db.commit()
    return {"message": "Demande supprimée avec succès"}
