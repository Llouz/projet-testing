# Résultats provisoires : version multi-agents

Ces essais portent sur des scénarios synthétiques. Le modèle Groq utilisé est `openai/gpt-oss-20b`. Les scénarios 11 à 13 et leurs références existaient avant ces essais ; ils restent en nombre insuffisant pour conclure sur la performance générale. La version multi-v2 utilise trois appels successifs (avec reprises limitées), alors que la version à un modèle utilisait un appel par tentative. Les prompts, les contraintes de format et les contextes diffèrent : la comparaison est indicative, pas une expérience contrôlée parfaite.

| Cas | Référence | Décision de l'agent 2 | Agent de vérification | Résultat |
| --- | --- | --- | --- | --- |
| 11 : champ renommé | repair_test | needs_review | Échec API 429 après reprises | Décision incorrecte selon la référence ; chaîne incomplète. |
| 12 : commandes d'autres pharmacies | report_bug | repair_test | needs_review | L'agent 2 décrit le bug mais le classe incorrectement ; le vérificateur demande une revue. |
| 13 : quantité égale au stock | needs_review | repair_test | Échec API 429 après reprises | Décision incorrecte selon la référence ; chaîne incomplète. |

Les résultats multi-v2 montrent **0 décision conforme sur 3 décisions de l'agent 2**, et **1 chaîne complète sur 3**. Les précédentes premières réponses JSON de la version à un modèle étaient conformes sur ces mêmes trois cas (3/3), mais la réparation du cas 11 n'était pas correcte au premier essai. Les deux mesures ne suffisent pas à conclure qu'une architecture est généralement meilleure.

## Appels et temps observés

- Cas 11 : 7 appels, dont 4 erreurs 429 et 1 erreur 400 ; environ 101,861 secondes cumulées par rôle, attentes comprises.
- Cas 12 : 5 appels, dont 2 erreurs 429 ; environ 34,324 secondes cumulées par rôle, attentes comprises.
- Cas 13 : 9 appels, dont 6 erreurs 429 et 1 erreur 400 ; environ 76,623 secondes cumulées par rôle, attentes comprises.

Ces durées couvrent les rôles et leurs attentes, mais pas la préparation initiale ni la revue humaine. Les appels supplémentaires résultent de reprises limitées après certaines erreurs. Le contenu du fichier `resultats/evaluation_v2.json` résume les résultats sans clé ; les journaux détaillés locaux figurent dans `executions/`, qui n'est pas suivi par Git.

## Limites et décision prudente

Le modèle peut produire un JSON valide mais une décision incorrecte. Il peut classer une correction du code comme une réparation du test. Un agent de vérification utilisant le même modèle n'est pas une garantie d'indépendance ou de justesse. Une preuve citée ou une suite verte ne suffit pas non plus à démontrer une bonne réparation.

Après ces essais, le prototype a été ajusté : si le vérificateur refuse une proposition ou demande une revue, la décision effective est `needs_review`, avec validation humaine obligatoire. Cet ajustement est vérifié par test simulé et n'a pas été évalué de nouveau sur ces appels réels. Le prototype ne modifie pas les tests automatiquement et ne compare pas encore les corrections par exécution automatique ; une validation manuelle reste nécessaire.

## Préparation de multi-v3

La version multi-v3, préparée après les résultats ci-dessus, clarifie les catégories et demande une citation pour les décisions `repair_test` et `report_bug`. Un contrôle textuel vérifie que la citation figure parmi les règles fournies ; une citation absente ou un avis négatif du vérificateur impose une revue humaine. Le contrôle textuel ne prouve ni la pertinence ni la validité du raisonnement. Les 21 tests locaux passent, y compris des scénarios simulés de citation absente et de désaccord. L'effet de multi-v3 sur des appels réels et sur les quotas n'a pas encore été mesuré.

## Essais réels de multi-v3

Trois nouvelles exécutions ont été réalisées avec `openai/gpt-oss-20b`, après modification des consignes. Les scénarios 11 à 13 sont les mêmes que précédemment : ils ont servi au développement et ne constituent plus une évaluation indépendante de la version v3.

| Cas | Référence | Proposition agent 2 | Vérification et décision effective | Observation |
| --- | --- | --- | --- | --- |
| 11 | repair_test | repair_test | Vérificateur `needs_review`, décision effective `needs_review` | Décision proposée correcte mais revue supplémentaire ; correction rejouée : 5/6 tests, incomplète. |
| 12 | report_bug | report_bug | Chaîne incomplète : quota lors de la vérification ; aucune décision effective | Décision proposée correcte mais preuve fournie à null et vérificateur indisponible. |
| 13 | needs_review | report_bug | Vérificateur `accept` ; citation non retrouvée et décision effective `needs_review` | Décision proposée erronée ; la revue est imposée par le contrôle textuel, malgré l'accord du vérificateur. |

Sur les **3 décisions proposées**, 2 correspondent aux références. Sur les **2 chaînes complètes**, la décision effective correspond à la référence dans 1 cas sur 2 : le cas 11 est envoyé à la revue malgré une décision initiale correcte ; le cas 13 est envoyé à la revue après contrôle de citation. La chaîne du cas 12 ne donne aucune décision effective. Ces indicateurs distincts ne mesurent pas directement une réparation correcte.

La correction du cas 11 a été rejouée dans une copie temporaire via `verifier_11_v3.py` : le test du distributeur inexistant échoue, car l'ancien nom de champ reste utilisé dans le paramètre du test. Le code actif n'a pas été modifié.

Nombre d'appels et durée cumulée des rôles, avec attentes de reprise, sans préparation ni revue humaine :

- 11 : 5 appels, 2 erreurs HTTP 429, environ 44,824 secondes ;
- 12 : 8 appels, 5 erreurs HTTP 429 et 1 erreur HTTP 400, environ 55,539 secondes ;
- 13 : 9 appels, 5 erreurs HTTP 429 et 1 erreur HTTP 400, environ 86,997 secondes.

Le coût de la validation humaine et les éventuels coûts financiers n'ont pas été mesurés. Un contrôle qui constate simplement la présence d'une citation ne peut pas prouver que la règle citée est pertinente ou que le modèle raisonne correctement. Les réponses et limites sont résumées sans clé dans `resultats/evaluation_v3.json` ; les journaux détaillés restent locaux et ignorés par Git.
