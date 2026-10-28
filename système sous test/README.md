# Réparation de tests assistée par IA

Projet de test logiciel appliqué à une application de gestion de médicaments avec backend FastAPI et interface React. Les expériences ciblent les fonctions de commandes de pharmacie dans le backend.

Le programme prépare une évolution dans une copie temporaire, exécute les tests pytest, puis transmet le code pertinent, le diff et l'échec à un modèle via API. Il demande de distinguer un test obsolète d'un bug. Les propositions sont revues et certaines sont rejouées manuellement. Les tests utilisent SQLite en mémoire et n'exercent ni les routes HTTP ni l'authentification complète.

- [Installation et reproduction](analyse_ia/README.md)
- [Résultats et limites](analyse_ia/BILAN.md)
- [Premiers essais](analyse_ia/journal_initial.md)
- [Scénarios](scenarios/)

Ne jamais publier de clés ou de données confidentielles. Avant tout partage, vérifier l'ensemble du dépôt, y compris la configuration de connexion à la base et les copies de code dans les scénarios.

## Configuration de démonstration

Les identifiants du projet d'origine ont été remplacés dans cette copie. Sans configuration, le backend utilise une base SQLite locale de démonstration et une clé de développement non secrète. Pour une installation personnelle, définir `DATABASE_URL` et `APP_SECRET_KEY` par des variables d'environnement ; ne pas publier leurs valeurs. Les comptes créés par `backend/init_admin.py` sont des données fictives et ne conviennent pas à la production. Les tests utilisent leur propre base SQLite en mémoire.

Le répertoire `presentation/` contient le rapport et le guide de démonstration.
