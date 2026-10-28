from backend.database import SessionLocale
from backend.models import Utilisateur


def creer_utilisateurs_defaut():
    db = SessionLocale()
    
    utilisateurs = [
        {
            "nom": "Pharmacie Centrale",
            "email": 'demo-11@example.invalid',
            "mot_de_passe": 'mot-de-passe-demo',
            "type_utilisateur": "admin"
        },
        {
            "nom": "Distributeur Test",
            "email": 'demo-17@example.invalid',
            "mot_de_passe": 'mot-de-passe-demo',
            "type_utilisateur": "distributeur"
        },
        {
            "nom": "Fabricant Test",
            "email": 'demo-23@example.invalid',
            "mot_de_passe": 'mot-de-passe-demo',
            "type_utilisateur": "fabricant"
        },
        {
            "nom": "Livreur Test",
            "email": 'demo-29@example.invalid',
            "mot_de_passe": 'mot-de-passe-demo',
            "type_utilisateur": "livreur"
        },
        {
            "nom": "Pharmacie Test",
            "email": 'demo-35@example.invalid',
            "mot_de_passe": 'mot-de-passe-demo',
            "type_utilisateur": "pharmacie"
        }
    ]
    
    for user_data in utilisateurs:
        existing = db.query(Utilisateur).filter_by(email=user_data["email"]).first()
        if existing:
            print(f"ℹ L'utilisateur {user_data['email']} existe déjà.")
            continue
        
        user = Utilisateur(
            nom=user_data["nom"],
            email=user_data["email"],
            mot_de_passe=user_data["mot_de_passe"],
            type_utilisateur=user_data["type_utilisateur"]
        )
        db.add(user)
        print(f"✔ Utilisateur {user_data['type_utilisateur']} créé : {user_data['email']}")
    
    db.commit()
    db.close()
    print("\n✔ Tous les comptes par défaut ont été créés avec succès !")

if __name__ == "__main__":
    creer_utilisateurs_defaut()
