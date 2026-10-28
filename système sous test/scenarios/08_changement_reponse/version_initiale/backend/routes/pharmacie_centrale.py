from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocale
from backend import models
from datetime import datetime
import qrcode
import os

admin_router = APIRouter(prefix="/admin", tags=["Pharmacie Centrale"])

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

@admin_router.get("/utilisateurs")
def voir_utilisateurs(db: Session = Depends(get_db)):
    return db.query(models.Utilisateur).filter(models.Utilisateur.type_utilisateur != "livreur").all()

@admin_router.get("/demandes-comptes")
def voir_demandes_comptes(db: Session = Depends(get_db)):
    return db.query(models.DemandeCreationCompte).filter(models.DemandeCreationCompte.type_utilisateur != "livreur").all()

@admin_router.post("/demandes-comptes/{id}/valider")
def valider_demande_compte(id: int, db: Session = Depends(get_db)):
    demande = db.query(models.DemandeCreationCompte).get(id)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    utilisateur = models.Utilisateur(
    nom=demande.nom,
    email=demande.email,
    mot_de_passe=demande.mot_de_passe, 
    type_utilisateur=demande.type_utilisateur
    )

    db.add(utilisateur)
    demande.statut = "acceptée"

    if demande.type_utilisateur == "pharmacie":
        stock = models.StockPharmacie(pharmacie=utilisateur, medicament_id=None, quantite=0)
        db.add(stock)
    elif demande.type_utilisateur == "distributeur":
        stock = models.StockDistributeur(distributeur=utilisateur, medicament_id=None, quantite=0, prix_unitaire=0)
        db.add(stock)

    db.commit()
    return {"message": "Compte validé et utilisateur créé"}

@admin_router.post("/demandes-comptes/{id}/refuser")
def refuser_demande_compte(id: int, db: Session = Depends(get_db)):
    demande = db.query(models.DemandeCreationCompte).get(id)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    demande.statut = "rejetée"
    db.commit()
    return {"message": "Demande rejetée"}

@admin_router.get("/stock")
def voir_stock_centrale(db: Session = Depends(get_db)):
    stock = db.query(models.StockPharmacieCentrale).all()
    resultat = []

    for ligne in stock:
        medicament = ligne.medicament 
        resultat.append({
            "medicament_id": ligne.medicament_id,
            "nom_medicament": medicament.nom if medicament else "Inconnu",
            "quantite": ligne.quantite
        })

    return resultat


@admin_router.get("/demandes-medicaments")
def voir_demandes_medicaments(db: Session = Depends(get_db)):
    return db.query(models.DemandeMedicament).all()

@admin_router.post("/demandes-medicaments/{id}/valider")
def valider_demande_medicament(id: int, db: Session = Depends(get_db)):
    demande = db.query(models.DemandeMedicament).get(id)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    nouveau_medicament = models.Medicament(
        nom=demande.nom,
        description=demande.description,
        origine="Inconnue",
        date_expiration=demande.date_expiration,
        statut="approuvé",
        chemin_qr=""
    )
    db.add(nouveau_medicament)
    db.commit()

    chemin = f"static/qrcodes/medicament_{nouveau_medicament.id}.png"
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    img = qrcode.make(f"Medicament ID: {nouveau_medicament.id} - {nouveau_medicament.nom}")
    img.save(chemin)

    nouveau_medicament.chemin_qr = chemin
    db.commit()

    stock = db.query(models.StockPharmacieCentrale).filter_by(medicament_id=nouveau_medicament.id).first()
    if stock:
        stock.quantite += demande.quantite
    else:
        stock = models.StockPharmacieCentrale(
            medicament_id=nouveau_medicament.id,
            quantite=demande.quantite,
        )
        db.add(stock)

    demande.statut = "acceptée"
    db.commit()

    return {"message": "Médicament accepté, QR généré et stock mis à jour."}


@admin_router.post("/demandes-medicaments/{id}/refuser")
def refuser_demande_medicament(id: int, db: Session = Depends(get_db)):
    demande = db.query(models.DemandeMedicament).get(id)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    demande.statut = "rejetée"
    db.commit()
    return {"message": "Demande de médicament rejetée."}

@admin_router.get("/demandes-stock-distributeurs")
def voir_demandes_stock_distributeurs(db: Session = Depends(get_db)):
    demandes = db.query(models.CommandeDistributeur).filter(models.CommandeDistributeur.statut == "en_attente").all()
    resultat = []

    for d in demandes:
        medicament = d.medicament  
        distributeur = d.distributeur  
        resultat.append({
            "id": d.id,
            "distributeur_id": d.distributeur_id,
            "nom_distributeur": distributeur.nom if distributeur else "Inconnu",
            "medicament_id": d.medicament_id,
            "nom_medicament": medicament.nom if medicament else "Inconnu",
            "quantite": d.quantite,
            "statut": d.statut
        })

    return resultat


@admin_router.post("/demandes-stock-distributeurs/{id}/valider")
def valider_demande_stock_distributeur(id: int, db: Session = Depends(get_db)):
    demande = db.query(models.CommandeDistributeur).get(id)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    stock_centrale = db.query(models.StockPharmacieCentrale).filter_by(medicament_id=demande.medicament_id).first()
    if not stock_centrale or stock_centrale.quantite < demande.quantite:
        raise HTTPException(status_code=400, detail="Quantité insuffisante en stock central")

    stock_centrale.quantite -= demande.quantite

    stock_distributeur = db.query(models.StockDistributeur).filter_by(
        distributeur_id=demande.distributeur_id,
        medicament_id=demande.medicament_id
    ).first()

    if stock_distributeur:
        stock_distributeur.quantite += demande.quantite
    else:
        db.add(models.StockDistributeur(
            distributeur_id=demande.distributeur_id,
            medicament_id=demande.medicament_id,
            quantite=demande.quantite,
            prix_unitaire=0
        ))

    demande.statut = "acceptée"
    db.commit()
    return {"message": "Demande de stock acceptée et stock mis à jour"}

@admin_router.post("/demandes-stock-distributeurs/{id}/refuser")
def refuser_demande_stock_distributeur(id: int, db: Session = Depends(get_db)):
    demande = db.query(models.CommandeDistributeur).get(id)
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    demande.statut = "rejetée"
    db.commit()
    return {"message": "Demande de stock rejetée"}
