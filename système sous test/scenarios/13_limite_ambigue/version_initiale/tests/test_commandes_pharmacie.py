"""Tests des fonctions de commande, avec une base SQLite isolée en mémoire."""
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models
from backend.database import Base
from backend.routes.pharmacie import CommandeRequest, commander, confirmer_reception


@pytest.fixture
def db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        models.Utilisateur(id=1, nom='Pharmacie', type_utilisateur='pharmacie'),
        models.Utilisateur(id=2, nom='Distributeur', type_utilisateur='distributeur'),
        models.Medicament(id=1, nom='Medicament test'),
        models.StockDistributeur(distributeur_id=2, medicament_id=1, quantite=10, prix_unitaire=5),
    ])
    session.commit()
    yield session
    session.close()
    engine.dispose()


def demande(**changes):
    valeurs = {'medicament_id': 1, 'quantite': 3, 'distributeur_id': 2}
    valeurs.update(changes)
    return CommandeRequest(**valeurs)


def test_commande_valide(db):
    resultat = commander(demande(), db, pharmacie_id=1)
    commande = db.query(models.CommandePharmacie).one()
    assert resultat['commande'].id == commande.id
    assert (commande.pharmacie_id, commande.medicament_id, commande.quantite, commande.statut) == (1, 1, 3, 'en_attente')


@pytest.mark.parametrize(('modification', 'code', 'detail'), [
    ({'distributeur_id': 999}, 404, 'Distributeur non trouvé'),
    ({'medicament_id': 999}, 404, 'Médicament non trouvé'),
    ({'quantite': 11}, 400, 'Stock insuffisant chez le distributeur'),
])
def test_commande_refusee(db, modification, code, detail):
    with pytest.raises(HTTPException) as erreur:
        commander(demande(**modification), db, pharmacie_id=1)
    assert erreur.value.status_code == code
    assert erreur.value.detail == detail
    assert db.query(models.CommandePharmacie).count() == 0


def test_reception_ajoute_au_stock_existant(db):
    db.add(models.StockPharmacie(pharmacie_id=1, medicament_id=1, quantite=4))
    commande = models.CommandePharmacie(pharmacie_id=1, distributeur_id=2, medicament_id=1, quantite=3, statut='validée')
    db.add(commande)
    db.commit()
    confirmer_reception(commande.id, db, pharmacie_id=1)
    assert db.query(models.StockPharmacie).one().quantite == 7
    assert commande.statut == 'reçue'


def test_reception_refusee_si_non_validee(db):
    commande = models.CommandePharmacie(pharmacie_id=1, distributeur_id=2, medicament_id=1, quantite=3, statut='en_attente')
    db.add(commande)
    db.commit()
    with pytest.raises(HTTPException) as erreur:
        confirmer_reception(commande.id, db, pharmacie_id=1)
    assert erreur.value.status_code == 400
    assert commande.statut == 'en_attente'
    assert db.query(models.StockPharmacie).count() == 0


def test_commande_egale_au_stock_disponible(db):
    resultat = commander(demande(quantite=10), db, pharmacie_id=1)
    assert resultat['commande'].quantite == 10
    assert resultat['commande'].statut == 'en_attente'
