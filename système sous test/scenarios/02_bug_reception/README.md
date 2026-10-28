# Cas 02 — Un bug lors de la réception d'une commande

## Règle utilisée
Une commande validée dont la réception est confirmée doit passer au statut « reçue », en plus de mettre à jour le stock. C'est le comportement de la version initiale retenue pour ce scénario.

## Expérience
1. La version initiale passe les six tests.
2. Une modification volontaire met la commande au statut « en_attente » après réception. Le test de réception échoue : c'est un défaut du code.
3. Une fausse réparation modifie l'assertion pour attendre « en_attente ». Les tests passent alors, mais le défaut reste présent : il est masqué.

La décision de référence est de **signaler le bug et de conserver le test initial**. La modification du test à l'étape 3 est volontairement incorrecte et sert uniquement à illustrer le risque. Aucune IA n'est utilisée dans cette démonstration.

Depuis la racine du projet, avec les dépendances du backend et pytest installés :

```bash
venv/bin/python scenarios/02_bug_reception/demo.py
```

L'expérience utilise une copie temporaire et SQLite en mémoire. Elle ne modifie pas l'application active ni PostgreSQL. Ces tests appellent les fonctions directement, sans tester HTTP ou l'authentification. Les différences sont produites par Python ; l'intégration à Git et à un modèle d'IA reste à faire.
