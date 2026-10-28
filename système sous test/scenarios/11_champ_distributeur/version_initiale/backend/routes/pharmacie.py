from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocale
from backend import models
from backend.routes.auth import get_current_user

pharmacie_router = APIRouter(prefix="/pharmacie", tags=["Pharmacie"])

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()


def get_pharmacie_id(user=Depends(get_current_user)):
    if user.type_utilisateur != "pharmacie":
        raise HTTPException(status_code=403, detail="Accès réservé aux pharmacies")
    return user.id

class CommandeRequest(BaseModel):
    medicament_id: int
    quantite: int
    distributeur_id: int

@pharmacie_router.get("/infos")
def infos(db: Session = Depends(get_db), pharmacie_id: int = Depends(get_pharmacie_id)):
    user = db.query(models.Utilisateur).get(pharmacie_id)
    if not user or user.type_utilisateur != "pharmacie":
        raise HTTPException(status_code=404, detail="Pharmacie non trouvée")
    return user

@pharmacie_router.get("/stock")
def voir_stock(db: Session = Depends(get_db), pharmacie_id: int = Depends(get_pharmacie_id)):
    stock = db.query(models.StockPharmacie).filter_by(pharmacie_id=pharmacie_id).all()

    result = []
    for item in stock:
        result.append({
            "id": item.id,
            "quantite": item.quantite,
            "medicament_id": item.medicament_id,
            "nom_medicament": item.medicament.nom if item.medicament else None
        })
    
    return result

@pharmacie_router.get("/catalogues")
def voir_catalogues(db: Session = Depends(get_db)):
    stocks = db.query(models.StockDistributeur).filter(models.StockDistributeur.prix_unitaire != None).all()
    resultats = []
    for stock in stocks:
        if stock.medicament:  # s'assurer que la relation existe
            resultats.append({
                "id": stock.id,
                "quantite": stock.quantite,
                "prix_unitaire": stock.prix_unitaire,
                "medicament_id": stock.medicament_id,
                "nom_medicament": stock.medicament.nom,
                "distributeur_id": stock.distributeur_id  # ✅ ici on ajoute
            })
        else:
            print(f"[WARN] Le stock ID={stock.id} n'a pas de médicament associé.")
    return resultats

# 4. Commander un médicament
@pharmacie_router.post("/commandes")
def commander(data: CommandeRequest, db: Session = Depends(get_db), pharmacie_id: int = Depends(get_pharmacie_id)):
    distributeur = db.query(models.Utilisateur).get(data.distributeur_id)
    if not distributeur or distributeur.type_utilisateur != "distributeur":
        raise HTTPException(status_code=404, detail="Distributeur non trouvé")

    medicament = db.query(models.Medicament).get(data.medicament_id)
    if not medicament:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")

    stock = db.query(models.StockDistributeur).filter_by(
        distributeur_id=data.distributeur_id,
        medicament_id=data.medicament_id
    ).first()

    if not stock or stock.quantite < data.quantite:
        raise HTTPException(status_code=400, detail="Stock insuffisant chez le distributeur")

    commande = models.CommandePharmacie(
        pharmacie_id=pharmacie_id,
        medicament_id=data.medicament_id,
        quantite=data.quantite,
        distributeur_id=data.distributeur_id,
        statut="en_attente"
    )
    db.add(commande)
    db.commit()
    db.refresh(commande)
    return {"message": "Commande envoyée au distributeur", "commande": commande}


@pharmacie_router.get("/commandes")
def voir_commandes(db: Session = Depends(get_db), pharmacie_id: int = Depends(get_pharmacie_id)):
    return db.query(models.CommandePharmacie).filter_by(pharmacie_id=pharmacie_id).all()

@pharmacie_router.post("/commandes/{id}/confirmer-reception")
def confirmer_reception(id: int, db: Session = Depends(get_db), pharmacie_id: int = Depends(get_pharmacie_id)):
    commande = db.query(models.CommandePharmacie).get(id)
    if not commande or commande.pharmacie_id != pharmacie_id:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    if commande.statut != "validée":
        raise HTTPException(status_code=400, detail="Commande non encore livrée")

    stock = db.query(models.StockPharmacie).filter_by(pharmacie_id=pharmacie_id, medicament_id=commande.medicament_id).first()
    if stock:
        stock.quantite += commande.quantite
    else:
        db.add(models.StockPharmacie(pharmacie_id=pharmacie_id, medicament_id=commande.medicament_id, quantite=commande.quantite))

    commande.statut = "reçue"
    db.commit()
    return {"message": "Commande reçue et stock mis à jour"}
