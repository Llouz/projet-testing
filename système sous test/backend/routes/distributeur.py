from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database import SessionLocale
from backend import models
from backend.utils.jwt_utils import verifier_token
from pydantic import BaseModel
from typing import Optional
from backend.routes.auth import get_current_user

distributeur_router = APIRouter(prefix="/distributeur", tags=["Distributeur"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

def get_distributeur_id(user=Depends(get_current_user)):
    if user.type_utilisateur != "distributeur":
        raise HTTPException(status_code=403, detail="Accès réservé aux distributeurs")
    return user.id

# Schémas
class DemandeStock(BaseModel):
    medicament_id: int
    quantite: int

class MiseAJourPrix(BaseModel):
    medicament_id: int
    prix_unitaire: float

class AttributionLivreur(BaseModel):
    livraison_id: int
    livreur_id: int

@distributeur_router.get("/infos")
def infos(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    user = db.query(models.Utilisateur).get(id_distributeur)
    if not user:
        raise HTTPException(status_code=404, detail="Distributeur non trouvé")
    return user

@distributeur_router.get("/stock")
def voir_stock(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    stocks = db.query(models.StockDistributeur).filter_by(distributeur_id=id_distributeur).all()
    resultats = []
    for stock in stocks:
        medicament = db.query(models.Medicament).get(stock.medicament_id)
        resultats.append({
            "medicament_id": stock.medicament_id,
            "nom": medicament.nom if medicament else "Inconnu",
            "quantite": stock.quantite,
            "prix_unitaire": stock.prix_unitaire
        })

    return resultats


@distributeur_router.put("/stock/prix")
def definir_ou_modifier_prix(data: MiseAJourPrix, db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    stock = db.query(models.StockDistributeur).filter_by(distributeur_id=id_distributeur, medicament_id=data.medicament_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Ce médicament n est pas dans votre stock")
    stock.prix_unitaire = data.prix_unitaire
    db.commit()
    return {"message": "Prix mis à jour", "stock": stock}

@distributeur_router.get("/catalogue")
def voir_catalogue(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    return db.query(models.StockDistributeur).filter_by(distributeur_id=id_distributeur).filter(models.StockDistributeur.prix_unitaire != None).all()

@distributeur_router.get("/commandes-stock")
def voir_commandes_stock(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    return db.query(models.CommandeDistributeur).filter_by(distributeur_id=id_distributeur).all()

@distributeur_router.post("/commandes-stock")
def commander_stock(data: DemandeStock, db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    medicament = db.query(models.Medicament).get(data.medicament_id)
    if not medicament:
        raise HTTPException(status_code=404, detail="Médicament inexistant")

    commande = models.CommandeDistributeur(
        distributeur_id=id_distributeur,
        medicament_id=data.medicament_id,
        quantite=data.quantite,
        statut="en_attente"
    )
    db.add(commande)
    db.commit()
    db.refresh(commande)
    return {"message": "Commande envoyée", "commande": commande}

@distributeur_router.get("/commandes-pharmacies")
def voir_commandes_pharmacies(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    commandes = (
        db.query(models.CommandePharmacie, models.Medicament.nom)
        .join(models.Medicament, models.CommandePharmacie.medicament_id == models.Medicament.id)
        .filter(models.CommandePharmacie.distributeur_id == id_distributeur, models.CommandePharmacie.statut == "en_attente")
        .all()
    )
    
    # commandes est une liste de tuples (CommandePharmacie, nom_medicament)
    result = []
    for commande, nom_medicament in commandes:
        result.append({
            "id": commande.id,
            "pharmacie_id": commande.pharmacie_id,
            "distributeur_id": commande.distributeur_id,
            "medicament_id": commande.medicament_id,
            "quantite": commande.quantite,
            "statut": commande.statut,
            "nom_medicament": nom_medicament
        })
    return result

@distributeur_router.post("/commandes-pharmacies/{id}/valider")
def valider_commande_pharmacie(id: int, db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    commande = db.query(models.CommandePharmacie).get(id)
    if not commande or commande.distributeur_id != id_distributeur:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    stock = db.query(models.StockDistributeur).filter_by(distributeur_id=id_distributeur, medicament_id=commande.medicament_id).first()
    if not stock or stock.quantite < commande.quantite:
        raise HTTPException(status_code=400, detail="Stock insuffisant")

    stock.quantite -= commande.quantite
    commande.statut = "validée"
    db.commit()

    livraison = models.Livraison(
        commande_id=commande.id,
        livreur_id=None,
        etat="en_attente",
        qr_code_chemin=""
    )
    db.add(livraison)
    db.commit()

    return {"message": "Commande validée et livraison créée", "livraison": livraison}

@distributeur_router.post("/commandes-pharmacies/{id}/refuser")
def refuser_commande_pharmacie(id: int, db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    commande = db.query(models.CommandePharmacie).get(id)
    if not commande or commande.distributeur_id != id_distributeur:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    commande.statut = "rejetée"
    db.commit()
    return {"message": "Commande refusée"}


@distributeur_router.post("/livraisons/attribuer-livreur")
def attribuer_livreur(data: AttributionLivreur, db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    livraison = db.query(models.Livraison).get(data.livraison_id)
    if not livraison or livraison.livreur_id is not None:
        raise HTTPException(status_code=404, detail="Livraison introuvable ou déjà assignée")

    commande = db.query(models.CommandePharmacie).get(livraison.commande_id)
    if not commande or commande.distributeur_id != id_distributeur:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas modifier cette livraison")

    livreur = db.query(models.Livreur).filter_by(id=data.livreur_id, distributeur_id=id_distributeur).first()
    if not livreur:
        raise HTTPException(status_code=404, detail="Livreur introuvable")

    livraison.livreur_id = data.livreur_id
    livraison.etat = "en_cours"  
    db.commit()
    return {"message": "Livreur assigné avec succès", "livraison": livraison}

@distributeur_router.get("/livraisons")
def voir_livraisons(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    livreurs = db.query(models.Livreur).filter_by(distributeur_id=id_distributeur).all()
    livreur_ids = [l.id for l in livreurs]

    commandes = db.query(models.CommandePharmacie).filter_by(distributeur_id=id_distributeur).all()
    commande_ids = [c.id for c in commandes]

    livraisons = db.query(models.Livraison).filter(models.Livraison.commande_id.in_(commande_ids)).all()
    return livraisons

@distributeur_router.get("/demandes-livreurs")
def voir_demandes_livreurs(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    return db.query(models.DemandeLivreur).filter_by(distributeur_id=id_distributeur, statut="en_attente").all()

@distributeur_router.post("/demandes-livreurs/{id}/valider")
def valider_livreur(id: int, db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    demande = db.query(models.DemandeLivreur).get(id)
    if not demande or demande.distributeur_id != id_distributeur:
        raise HTTPException(status_code=404, detail="Demande introuvable")

    livreur = models.Livreur(
        nom=demande.nom,
        email=demande.email,
        mot_de_passe=demande.mot_de_passe,
        distributeur_id=demande.distributeur_id
    )
    db.add(livreur)
    demande.statut = "acceptée"
    db.commit()
    return {"message": "Livreur accepté", "livreur": livreur}

@distributeur_router.post("/demandes-livreurs/{id}/refuser")
def refuser_livreur(id: int, db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    demande = db.query(models.DemandeLivreur).get(id)
    if not demande or demande.distributeur_id != id_distributeur:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    demande.statut = "rejetée"
    db.commit()
    return {"message": "Demande refusée"}

@distributeur_router.get("/mes-livreurs")
def voir_livreurs_du_distributeur(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    livreurs = db.query(models.Livreur).filter_by(distributeur_id=id_distributeur).all()

    return [
        {
            "id": l.id,
            "nom": l.nom,
            "email": l.email
        }
        for l in livreurs
    ]

@distributeur_router.get("/stock-centrale")
def voir_stock_pharmacie_centrale(db: Session = Depends(get_db), id_distributeur: int = Depends(get_distributeur_id)):
    stock = db.query(models.StockPharmacieCentrale).all()

    resultats = []
    for item in stock:
        medicament = db.query(models.Medicament).get(item.medicament_id)
        if medicament:
            resultats.append({
                "id": medicament.id,
                "nom": medicament.nom
            })

    return resultats


