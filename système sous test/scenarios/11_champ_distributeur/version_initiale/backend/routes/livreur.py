from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocale
from backend import models
from backend.routes.auth import get_current_user 

livreur_router = APIRouter(prefix="/livreur", tags=["Livreur"])

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

def get_livreur_id(user=Depends(get_current_user)):
    if getattr(user, "type_utilisateur", None) != "livreur":
        raise HTTPException(status_code=403, detail="Accès réservé aux livreurs")
    return user.id

@livreur_router.get("/infos")
def voir_infos_livreur(
    db: Session = Depends(get_db),
    livreur_id: int = Depends(get_livreur_id)
):
    livreur = db.query(models.Livreur).get(livreur_id)
    if not livreur:
        raise HTTPException(status_code=404, detail="Livreur non trouvé")
    return livreur

@livreur_router.get("/mes-livraisons")
def voir_mes_livraisons(
    db: Session = Depends(get_db),
    livreur_id: int = Depends(get_livreur_id)
):
    return db.query(models.Livraison).filter_by(livreur_id=livreur_id).all()

@livreur_router.put("/livraisons/{id}/etat")
def changer_etat_livraison(
    id: int,
    nouvel_etat: str,  
    db: Session = Depends(get_db),
    livreur_id: int = Depends(get_livreur_id)
):
    livraison = db.query(models.Livraison).get(id)
    if not livraison or livraison.livreur_id != livreur_id:
        raise HTTPException(status_code=404, detail="Livraison non trouvée")
    
    livraison.etat = nouvel_etat
    db.commit()
    return {"message": f"État de la livraison mis à jour: {nouvel_etat}"}
