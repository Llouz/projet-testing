import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from backend.database import SessionLocale
from backend import models
from enum import Enum
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List


auth_router = APIRouter(tags=["Authentification"])

SECRET_KEY = os.environ.get("APP_SECRET_KEY", "cle-demo-non-secrete-a-remplacer")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()


class TypeUtilisateur(str, Enum):
    pharmacie = "pharmacie"
    distributeur = "distributeur"
    fabricant = "fabricant"


class DemandeInscription(BaseModel):
    nom: str
    email: EmailStr
    type_utilisateur: TypeUtilisateur
    mot_de_passe: str

class DistributeurInfo(BaseModel):
    id: int
    nom: str

@auth_router.post("/demandes-comptes")
def demander_creation_compte(data: DemandeInscription, db: Session = Depends(get_db)):
    deja_utilisateur = db.query(models.Utilisateur).filter_by(email=data.email).first()
    deja_demande = db.query(models.DemandeCreationCompte).filter_by(email=data.email, statut="en_attente").first()

    if deja_utilisateur:
        raise HTTPException(status_code=400, detail="Un compte avec cet email existe déjà.")
    if deja_demande:
        raise HTTPException(status_code=400, detail="Une demande avec cet email est déjà en attente.")

    demande = models.DemandeCreationCompte(
        nom=data.nom,
        email=data.email,
        type_utilisateur=data.type_utilisateur,
        mot_de_passe=data.mot_de_passe,
        statut="en_attente"
    )

    db.add(demande)
    db.commit()
    db.refresh(demande)
    return {
        "message": "Demande enregistrée avec succès. En attente de validation par la pharmacie centrale.",
        "demande": demande
    }


class DemandeLivreurInscription(BaseModel):
    nom: str
    email: EmailStr
    mot_de_passe: str
    distributeur_id: int


@auth_router.post("/demandes-livreur")
def demander_creation_livreur(data: DemandeLivreurInscription, db: Session = Depends(get_db)):
    distributeur = db.query(models.Utilisateur).filter_by(id=data.distributeur_id, type_utilisateur="distributeur").first()
    if not distributeur:
        raise HTTPException(status_code=400, detail="Distributeur introuvable.")

    deja_livreur = db.query(models.Livreur).filter_by(email=data.email).first()
    deja_demande = db.query(models.DemandeLivreur).filter_by(email=data.email, statut="en_attente").first()

    if deja_livreur:
        raise HTTPException(status_code=400, detail="Un livreur avec cet email existe déjà.")
    if deja_demande:
        raise HTTPException(status_code=400, detail="Une demande avec cet email est déjà en attente.")

    nouvelle_demande = models.DemandeLivreur(
        nom=data.nom,
        email=data.email,
        mot_de_passe=data.mot_de_passe,
        statut="en_attente",
        distributeur_id=data.distributeur_id
    )

    db.add(nouvelle_demande)
    db.commit()
    db.refresh(nouvelle_demande)

    return {
        "message": "Demande de création de compte livreur enregistrée avec succès.",
        "demande": nouvelle_demande
    }


class Token(BaseModel):
    access_token: str
    token_type: str


def creer_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@auth_router.post("/token", response_model=Token)
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter_by(email=form_data.username).first()
    if utilisateur and utilisateur.mot_de_passe == form_data.password:
        token = creer_token({
            "sub": utilisateur.email,
            "type_utilisateur": utilisateur.type_utilisateur,
            "id": utilisateur.id
        })
        return {"access_token": token, "token_type": "bearer"}

    livreur = db.query(models.Livreur).filter_by(email=form_data.username).first()
    if livreur and livreur.mot_de_passe == form_data.password:
        token = creer_token({
            "sub": livreur.email,
            "type_utilisateur": "livreur",
            "id": livreur.id,
            "distributeur_id": livreur.distributeur_id
        })
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Identifiants incorrects")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        type_utilisateur = payload.get("type_utilisateur")

        if not email:
            raise HTTPException(status_code=401, detail="Token invalide")

        if type_utilisateur == "livreur":
            user = db.query(models.Livreur).filter_by(email=email).first()
            if user:
                user.type_utilisateur = "livreur"
        else:
            user = db.query(models.Utilisateur).filter_by(email=email).first()

        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token expiré ou invalide")
    

@auth_router.get("/distributeurs", response_model=List[DistributeurInfo])
def lister_distributeurs(db: Session = Depends(get_db)):
    """
    Retourne la liste des utilisateurs de type 'distributeur' (id + nom).
    """
    distributeurs = db.query(models.Utilisateur).filter_by(type_utilisateur="distributeur").all()
    return [DistributeurInfo(id=d.id, nom=d.nom) for d in distributeurs]
