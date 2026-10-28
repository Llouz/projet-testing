# Premiers tests des commandes de pharmacie

Ces tests appellent directement les fonctions Python et utilisent SQLite en mémoire : ils ne se connectent pas à PostgreSQL et ne testent pas les requêtes HTTP ni l'authentification.

Depuis la racine du projet, dans un environnement Python contenant les dépendances du backend :

```bash
python -m pip install -r requirements-tests.txt
python -m pytest tests/test_commandes_pharmacie.py -q
```

Les tests vérifient la création d'une commande, trois refus et deux cas de réception. La règle concernant les quantités nulles ou négatives reste à confirmer avant d'en faire une exigence.
