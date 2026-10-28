from fastapi import FastAPI
from backend.database import moteur
import backend.models
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.pharmacie_centrale import admin_router
from backend.routes.distributeur import distributeur_router
from backend.routes.fabricant import fabricant_router
from backend.routes.auth import auth_router
from backend.routes.livreur import livreur_router
from backend.routes.pharmacie import pharmacie_router

backend.models.Base.metadata.create_all(bind=moteur)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

application = FastAPI()

application.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application.include_router(admin_router)
application.include_router(fabricant_router)
application.include_router(auth_router)
application.include_router(distributeur_router)
application.include_router(livreur_router)
application.include_router(pharmacie_router)

@application.get("/")
def accueil():
    return {"message": "Bienvenue"}
