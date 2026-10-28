# Conception du système multi-agents

## Objectif

Comparer la solution existante à un pipeline où plusieurs appels au modèle remplissent des rôles distincts. Le système doit distinguer une adaptation nécessaire des tests, un défaut du code et une situation nécessitant une revue humaine. Cette conception est un plan de réalisation : les agents décrits ici ne sont pas encore implémentés.

## Architecture proposée

```text
Scénario + règles + diff + résultat pytest
                   │
                   ▼
          1. Agent d'analyse
                   │ diagnostic structuré
                   ▼
      2. Agent de décision et réparation
                   │ décision + éventuelle correction
                   ▼
         3. Agent de vérification
                   │ avis indépendant sur les risques
                   ▼
      Orchestrateur : rapport et journal
```

Les trois agents peuvent utiliser le même modèle Groq avec des instructions et des appels distincts. Un agent correspond ici à un rôle et à un appel du modèle, pas à un processus autonome permanent. L'orchestrateur Python organise le flux et prépare les tests ; il n'est pas compté comme agent d'IA.

## Rôles et échanges

### 1. Agent d'analyse

- **Entrées :** test initial et échec pytest, diff, code pertinent, règles fournies.
- **Mission :** identifier la modification, le comportement testé et la règle pertinente ou manquante ; ne pas proposer de correction finale.
- **Sortie JSON :** `changement`, `comportement_teste`, `regle_necessaire`, `preuve_regle` (citation ou null), `informations_manquantes` (liste).

### 2. Agent de décision et de réparation

- **Entrées :** les mêmes éléments factuels et le diagnostic de l'agent 1.
- **Mission :** choisir `repair_test`, `report_bug` ou `needs_review`. Proposer une correction uniquement si le test est jugé obsolète. Conserver le contrôle métier et les assertions pertinentes.
- **Sortie JSON :** `decision`, `explication`, `correction_test` (correction ou null), `risques` (liste).

### 3. Agent de vérification

- **Entrées :** test initial, code et diff, règles et proposition complète de l'agent 2 ; si disponible, résultat d'exécution dans une copie isolée.
- **Mission :** vérifier si la décision est cohérente avec les règles, si une correction modifie ou supprime des vérifications, et si les informations suffisent. Signaler ses désaccords ; ne pas considérer une suite verte comme preuve suffisante.
- **Sortie JSON :** `avis` (`accept`, `reject`, `needs_review`), `motifs` (liste), `assertions_a_revoir` (liste), `questions` (liste).
- **Indépendance :** ne reçoit pas l'étiquette de référence des scénarios ni les conclusions attendues. Un second appel du même modèle peut partager ses erreurs : son avis ne remplace pas l'évaluation humaine.

## Orchestration et contrôle

1. Préparer une copie temporaire du scénario et lancer les tests.
2. Exécuter les trois rôles dans l'ordre et valider chaque objet JSON. Si un appel échoue ou si le format est invalide, enregistrer l'erreur et arrêter ou demander une revue, sans inventer de résultat.
3. Vérifier la présence textuelle des citations dans les règles fournies. La présence d'une citation ne prouve pas qu'elle est pertinente.
4. Une correction proposée peut être vérifiée dans une copie isolée, uniquement selon une méthode d'application explicite et contrôlée. La copie du projet actif n'est pas modifiée ; une exécution de code généré nécessite un environnement adapté. En cas de désaccord ou de règle manquante, privilégier la revue humaine.
5. Conserver les entrées, les prompts, les versions du modèle, les réponses, les erreurs, les temps et la décision finale. Ne pas enregistrer les clés API. Une suite qui passe n'est pas une preuve suffisante de bonne réparation.

Le premier prototype peut fonctionner en mode proposition et revue, comme la version existante. L'application automatique d'une correction et les tentatives supplémentaires seront ajoutées et évaluées séparément si elles sont effectivement implémentées.

## Évaluation comparative

- Conserver la branche `main` et ses résultats comme référence ; enregistrer les nouveaux résultats multi-agents séparément.
- Utiliser les mêmes scénarios, règles, modèle et conditions d'appel quand c'est possible ; documenter les différences de contexte et de prompt.
- Mesurer les décisions correctes, les bugs correctement signalés, les fausses réparations et les réparations réellement vérifiées. Donner les nombres et leurs dénominateurs.
- Mesurer les réponses valides, les erreurs et le nombre d'appels par scénario ; distinguer temps des appels, temps total et temps de revue humaine. Estimer les coûts seulement avec des données disponibles.
- Utiliser de nouveaux scénarios réservés à l'évaluation finale : les scénarios qui ont aidé à régler les prompts ne sont pas indépendants.
- Présenter les désaccords entre agents et les limites : quota Groq, erreurs partagées entre agents, manque de règle métier et risque de faire passer un test sans préserver son intention.

## Livrables du prototype

1. Une commande de lancement séparée de la version existante.
2. Trois prompts versionnés et un orchestrateur.
3. Des journaux séparés par exécution et par agent, sans clé API.
4. Des tests simulant les réponses API et les échecs ; aucune requête payante nécessaire pour ces tests.
5. Un tableau comparatif et un README de reproduction, sans présenter comme observé un résultat qui n'a pas été mesuré.
