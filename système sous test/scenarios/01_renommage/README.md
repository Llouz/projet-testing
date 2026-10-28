# Cas 01 — Renommage de la fonction de commande

La fonction Python `commander` est renommée `passer_commande`. La route HTTP et son comportement restent inchangés. L'ancien test importe encore le nom précédent : il devient obsolète. La correction de référence adapte uniquement cet import et les appels, sans modifier les assertions.

Depuis la racine du projet, avec les dépendances du backend et pytest installés :

```bash
venv/bin/python scenarios/01_renommage/demo.py
```

Le script crée une copie temporaire de la version initiale figée dans ce dossier. Il exécute les tests avant le changement, après le changement et après la correction de référence ; il affiche les différences. Il ne modifie ni le backend actif, ni les tests actifs, ni PostgreSQL. Cette correction est écrite à la main : elle sert de référence pour évaluer plus tard une proposition de l'IA. Il s'agit d'un test des fonctions, pas d'un test HTTP. Les différences sont produites ici avec Python ; l'intégration à Git et à un modèle d'IA reste à faire.
