# Comparaison des approches : un modèle et multi-agents

**Binôme :** Adam Ellouz et Maher Ben Ammar

**Classe :** GI3 S4

**Sujet :** Réparation automatique de tests assistée par IA

## 1. Les deux approches

| Aspect | Version à un modèle | Prototype multi-agents |
| --- | --- | --- |
| Organisation | Un appel au modèle analyse l'échec et propose une décision. | Trois rôles successifs : analyse, décision, vérification. |
| Modèle utilisé pour les essais | `openai/gpt-oss-20b` via Groq, prompt v5. | Le même modèle via Groq, prompts multi-v3 et schémas propres à chaque rôle. |
| Décisions possibles | Réparer le test, signaler un bug ou demander une revue. | L'agent de décision propose l'une des trois décisions ; un vérificateur donne ensuite son avis. |
| Garde-fous | Vérification du format et contrôle textuel des citations. | Vérification du format, avis du vérificateur et contrôle textuel de la citation. Un désaccord ou une citation absente impose une revue. |
| Corrections | Proposées, puis appliquées et vérifiées manuellement dans une copie temporaire pour les cas étudiés. | Proposées ; leur application et leur vérification restent manuelles dans le prototype actuel. |

Les rôles multi-agents sont des appels distincts au même modèle, et non des modèles nécessairement différents. Un même modèle peut reproduire ses erreurs dans plusieurs rôles.

## 2. Scénarios comparés

Les deux approches ont été essayées sur les mêmes trois scénarios synthétiques et avec les mêmes références :

| Scénario | Situation | Référence |
| --- | --- | --- |
| **11** | Un champ de requête est renommé avec une évolution d'interface approuvée. | `repair_test` |
| **12** | Le filtre de confidentialité des commandes d'une pharmacie est supprimé. | `report_bug` |
| **13** | La règle concernant une quantité égale au stock disponible n'est pas précisée. | `needs_review` |

Les consignes de la version multi-agents ont évolué après des observations sur ces scénarios : ils ne constituent donc plus un jeu d'évaluation indépendant pour multi-v3. Les prompts, les schémas JSON et les informations transmises diffèrent entre les deux approches. Ces résultats servent à étudier le prototype, pas à établir une supériorité générale.

## 3. Résultats par scénario

| Cas | Version à un modèle : première réponse JSON reçue | Multi-agents v3 : décision proposée | Avis du vérificateur et décision effective | Vérification supplémentaire |
| --- | --- | --- | --- | --- |
| **11** | `repair_test` : conforme | `repair_test` : conforme | `needs_review` ; décision effective `needs_review` | Dans les deux approches, la première correction étudiée ne suffit pas. La proposition multi-v3 a été rejouée : **5 tests sur 6 passent**. |
| **12** | `report_bug` : conforme | `report_bug` : conforme | Vérification interrompue par le quota ; **pas de décision effective** | La proposition multi-agents ne fournit pas la citation requise. |
| **13** | `needs_review` : conforme | `report_bug` : non conforme | Le vérificateur répond `accept`, mais le contrôle ne retrouve pas la citation ; décision effective `needs_review` | La revue est imposée par le contrôle textuel malgré un raisonnement erroné de l'agent de décision et du vérificateur. |

### Lecture des résultats

- **Décisions proposées conformes aux références :** 3 sur 3 premières réponses JSON reçues avec un modèle ; 2 sur 3 décisions proposées par l'agent de décision en multi-v3.
- **Décisions effectives multi-v3 :** sur deux chaînes complètes, 1 sur 2 correspond à la référence. La troisième chaîne est incomplète : elle n'est ni une décision correcte, ni une décision incorrecte.
- **Réparation du cas 11 :** la première proposition de chaque approche n'est pas satisfaisante. La version à un modèle a obtenu une correction passant 6 tests après deux retours manuels ; cette réparation ne doit pas être comptée comme une réussite du premier essai. La proposition multi-v3 vérifiée laisse un test en échec.

Un contrôle textuel de citation vérifie uniquement qu'un passage figure dans les règles fournies : il ne garantit pas que ce passage est pertinent. Une décision conforme ne prouve pas non plus qu'une correction fonctionne ou préserve les vérifications.

## 4. Appels et durées

| Mesure | Un modèle, v5 | Multi-agents, v3 |
| --- | --- | --- |
| Appels enregistrés pour les cas 11 à 13 | 6 : ils incluent deux retours sur le cas 11 et un refus temporaire pour le cas 13. | 22, y compris les reprises après erreurs. |
| Réponses / chaînes | 5 réponses JSON sur 6 appels. | 2 chaînes complètes sur 3 scénarios. |
| Temps | Moyenne de **0,922 s par appel** sur ces 6 appels. | Temps cumulés des rôles, attentes comprises : **44,824 s**, **55,539 s** et **86,997 s** pour les cas 11, 12 et 13. |

Ces durées ne sont **pas directement comparables** : la première est une moyenne par appel qui exclut l'attente entre les essais, alors que les secondes incluent les attentes entre reprises et couvrent plusieurs rôles. Elles ne comprennent ni le temps de préparation ni la revue humaine. Aucun coût financier ni temps de réparation manuelle complet n'a été mesuré.

## 5. Analyse critique

Le multi-agents permet de rendre visibles plusieurs étapes du raisonnement et d'obtenir un avis de vérification. Dans le cas 13, le contrôle de la preuve a conduit à demander une revue alors que les deux agents s'étaient trompés. Ce garde-fou n'est cependant pas une preuve de justesse et peut aussi être trop prudent, comme dans le cas 11.

Dans ces essais, le prototype multi-agents a demandé davantage d'appels et subi plusieurs limites de quota. Les trois scénarios sont trop peu nombreux pour conclure que l'approche à un modèle est meilleure en général, ou que la vérification multi-agents détecte toujours les erreurs.

Pour une évaluation plus solide, il faudrait figer les versions, préparer davantage de scénarios indépendants, répéter les essais, mesurer le temps complet et la revue humaine, puis vérifier toutes les corrections proposées sans affaiblir les assertions.

## 6. Sources des résultats

- `système sous test/analyse_ia/tentatives/` : tentatives enregistrées de la version à un modèle, y compris l'erreur de quota et les retours.
- `système sous test/multi_agents/resultats/evaluation_v3.json` et `système sous test/multi_agents/RESULTATS.md` : résumé des essais multi-agents.
- `système sous test/multi_agents/verifier_11_v3.py` : vérification locale de la proposition multi-v3 du scénario 11.
- `système sous test/analyse_ia/bilan_tentatives.py` : calcul des indicateurs des appels à un modèle.

Les journaux multi-agents détaillés sont locaux et ignorés par Git ; le fichier de résultats résumé est conservé dans le dépôt. Ne pas inclure de clé API dans les documents ou captures.
