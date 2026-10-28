# Prototype multi-agents

Ce prototype déclenche trois appels Groq successifs : analyse, décision, vérification. Les agents reçoivent les faits préparés à partir d'une copie temporaire du scénario. L'agent de décision reçoit le diagnostic ; l'agent de vérification reçoit la proposition et les faits originaux. Aucun agent ne reçoit la réponse de référence. Les sorties sont validées sur leur structure JSON, puis enregistrées avec prompts, temps d'appel et erreurs dans `multi_agents/executions/` (dossier ignoré par Git).

La validation ne démontre pas qu'une explication ou une preuve est correcte. Le prototype ne vérifie pas encore automatiquement les citations ni n'applique les corrections proposées. La décision du vérificateur est un avis du modèle, pas une validation humaine. L'exécution de la correction et l'évaluation restent manuelles.

Depuis le dossier `système sous test`, avec les dépendances backend et pytest installées :

```bash
python multi_agents/orchestrateur.py 11 --preparer
```

Cette commande prépare les faits sans réseau. Pour appeler Groq, configurer `GROQ_API_KEY` dans le terminal puis lancer :

```bash
python multi_agents/orchestrateur.py 11
```

Le modèle par défaut est `openai/gpt-oss-20b` ; il peut être modifié avec `--modele`. Chaque rôle peut effectuer jusqu'à quatre appels en cas de quota temporaire ou de réponse JSON rejetée ; chaque tentative et délai sont enregistrés. Le programme s'arrête en cas d'erreur persistante. Si le vérificateur refuse la proposition ou demande une revue, la décision effective devient needs_review ; une validation humaine est toujours nécessaire. Les limites de débit et les coûts éventuels dépendent du compte. Les réponses et faits envoyés peuvent contenir du code ; vérifier les droits et ne pas utiliser de secrets.

Pour tester sans connexion ni clé :

```bash
python -m pytest tests/test_multi_agents.py -q
```

Une première comparaison indicative est disponible dans RESULTATS.md. Garder les scénarios, modèles et conditions comparables, puis mesurer les décisions et réparations, le nombre d'appels et la durée ; distinguer appels, attente et validation humaine.

Pour les modèles `openai/gpt-oss-20b` et `openai/gpt-oss-120b`, le prototype demande désormais une sortie JSON avec schéma strict, distinct pour chaque rôle ; les autres modèles utilisent le mode JSON objet. Le format choisi est enregistré dans le journal. Le schéma aide à respecter le format, mais ne garantit pas la justesse des réponses et n'élimine pas les erreurs d'API ou de quota. Cette modification doit être prise en compte lors de la comparaison aux essais précédents.

## Consignes multi-v3

La version multi-v3 distingue explicitement un défaut du code (`report_bug`), une évolution d'interface approuvée qui rend le test obsolète (`repair_test`) et une règle insuffisante (`needs_review`). L'agent de décision renvoie `preuve_decision` : une citation exacte d'une règle ou d'une évolution approuvée, ou null. Le contrôle automatique compare la citation aux lignes des règles fournies ; il ne vérifie ni sa pertinence ni sa vérité. Si la citation manque pour une décision autre que needs_review, ou si le vérificateur ne l'accepte pas, la décision effective est needs_review. Une revue humaine reste nécessaire même lorsque le contrôle réussit. Ces garde-fous sont testés localement ; leur effet réel doit être mesuré par de nouveaux appels.
