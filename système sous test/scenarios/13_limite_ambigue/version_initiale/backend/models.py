from sqlalchemy import Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    email = Column(String, unique=True, index=True)
    mot_de_passe = Column(String)
    type_utilisateur = Column(String)  
    distributeur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)  

    livreurs = relationship("Utilisateur", backref="distributeur", remote_side=[id])
    demandes_comptes = relationship("DemandeCreationCompte", back_populates="utilisateur")
    demandes_medicaments = relationship("DemandeMedicament", back_populates="fabricant")
    stock_pharmacie = relationship("StockPharmacie", back_populates="pharmacie")
    stock_distributeur = relationship("StockDistributeur", back_populates="distributeur")
    commandes_pharmacie = relationship("CommandePharmacie", back_populates="pharmacie", foreign_keys="CommandePharmacie.pharmacie_id")
    commandes_reçues = relationship("CommandePharmacie", back_populates="distributeur", foreign_keys="CommandePharmacie.distributeur_id")
    commandes_distributeur = relationship("CommandeDistributeur", back_populates="distributeur")
    livraisons = relationship("Livraison", back_populates="livreur")
    demandes_livreurs = relationship("DemandeLivreur", back_populates="distributeur")
    livreurs = relationship("Livreur", back_populates="distributeur")



class DemandeCreationCompte(Base):
    __tablename__ = "demandes_creation_compte"

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    email = Column(String)  
    type_utilisateur = Column(String)  
    justificatif = Column(String)
    statut = Column(String) 
    mot_de_passe = Column(String)

    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    utilisateur = relationship("Utilisateur", back_populates="demandes_comptes")


class Medicament(Base):
    __tablename__ = "medicaments"

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    description = Column(String)
    origine = Column(String)
    date_expiration = Column(Date)
    statut = Column(String)  
    chemin_qr = Column(String)

class StockPharmacieCentrale(Base):
    __tablename__ = "stock_pharmacie_centrale"

    id = Column(Integer, primary_key=True)
    medicament_id = Column(Integer, ForeignKey("medicaments.id"))
    quantite = Column(Integer)

    medicament = relationship("Medicament")


class DemandeMedicament(Base):
    __tablename__ = "demandes_medicaments"

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    description = Column(String)
    date_expiration = Column(Date)
    quantite = Column(Integer)
    statut = Column(String) 

    id_fabricant = Column(Integer, ForeignKey("utilisateurs.id"))
    fabricant = relationship("Utilisateur", back_populates="demandes_medicaments")


class CommandeDistributeur(Base):
    __tablename__ = "commandes_distributeurs"

    id = Column(Integer, primary_key=True)
    distributeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    medicament_id = Column(Integer, ForeignKey("medicaments.id"))
    quantite = Column(Integer)
    statut = Column(String)

    distributeur = relationship("Utilisateur", back_populates="commandes_distributeur")
    medicament = relationship("Medicament")



class StockDistributeur(Base):
    __tablename__ = "stock_distributeur"

    id = Column(Integer, primary_key=True)
    distributeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    medicament_id = Column(Integer, ForeignKey("medicaments.id"))
    quantite = Column(Integer)
    prix_unitaire = Column(Float, nullable=False)


    distributeur = relationship("Utilisateur", back_populates="stock_distributeur")
    medicament = relationship("Medicament")


class StockPharmacie(Base):
    __tablename__ = "stock_pharmacie"

    id = Column(Integer, primary_key=True)
    pharmacie_id = Column(Integer, ForeignKey("utilisateurs.id"))
    medicament_id = Column(Integer, ForeignKey("medicaments.id"))
    quantite = Column(Integer)

    pharmacie = relationship("Utilisateur", back_populates="stock_pharmacie")
    medicament = relationship("Medicament")  


class CommandePharmacie(Base):
    __tablename__ = "commandes_pharmacies"

    id = Column(Integer, primary_key=True)
    pharmacie_id = Column(Integer, ForeignKey("utilisateurs.id"))
    distributeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    medicament_id = Column(Integer, ForeignKey("medicaments.id"))
    quantite = Column(Integer)
    statut = Column(String)

    pharmacie = relationship("Utilisateur", back_populates="commandes_pharmacie", foreign_keys=[pharmacie_id])
    distributeur = relationship("Utilisateur", back_populates="commandes_reçues", foreign_keys=[distributeur_id])


class Livraison(Base):
    __tablename__ = "livraisons"

    id = Column(Integer, primary_key=True)
    commande_id = Column(Integer, ForeignKey("commandes_pharmacies.id"))
    livreur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    etat = Column(String) 
    qr_code_chemin = Column(String)

    livreur = relationship("Utilisateur", back_populates="livraisons")
    commande = relationship("CommandePharmacie")


class DemandeLivreur(Base):
    __tablename__ = "demandes_livreurs"

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    email = Column(String, unique=True)
    mot_de_passe = Column(String)
    statut = Column(String)

    distributeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    distributeur = relationship("Utilisateur", back_populates="demandes_livreurs")


class Livreur(Base):
    __tablename__ = "livreurs"

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    email = Column(String, unique=True)
    mot_de_passe = Column(String)
    distributeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    
    distributeur = relationship("Utilisateur", back_populates="livreurs")

