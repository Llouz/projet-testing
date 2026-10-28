import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = os.environ.get("APP_SECRET_KEY", "cle-demo-non-secrete-a-remplacer")
ALGORITHME = "HS256"
DUREE_VALIDITE = timedelta(days=1)

def creer_token(data: dict) -> str:
    donnees_a_encoder = data.copy()
    expiration = datetime.utcnow() + DUREE_VALIDITE
    donnees_a_encoder.update({"exp": expiration})
    return jwt.encode(donnees_a_encoder, SECRET_KEY, algorithm=ALGORITHME)

def verifier_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHME])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")
