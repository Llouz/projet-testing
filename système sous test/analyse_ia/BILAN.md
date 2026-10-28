# Bilan provisoire des expériences

## Méthode

Les résultats v2 enregistrés utilisent Groq et le modèle `openai/gpt-oss-20b`. Une réponse par scénario est retenue ci-dessous : la première réponse JSON enregistrée. Les réponses réussies et leurs prompts complets se trouvent dans `resultats/`. Les scripts d'analyse préparent les échecs dans des copies temporaires et n'appliquent pas automatiquement les corrections proposées. Les tests appellent directement les fonctions Python avec SQLite en mémoire, sans couvrir la couche HTTP ou l'authentification complète.

Les scénarios 01 et 02 ont servi à adapter le prompt ; 03 à 06 ont été essayés ensuite. Ces derniers restent peu nombreux, certains sont similaires aux premiers, et la règle métier pertinente est fournie au modèle. Les modifications et défauts sont artificiels. Ce bilan ne démontre donc pas la fiabilité du système sur des projets réels.

## Résultats

| Cas | Situation | Référence | Décision initiale v2 | Vérification et limites |
| --- | --- | --- | --- | --- |
| 01 | Fonction de commande renommée | repair_test | repair_test | Correction par alias rejouée : 6/6 tests passent, assertions conservées. |
| 02 | Statut erroné après réception | report_bug | report_bug | Décision correcte ; champ correction_test nul. |
| 03 | Fonction de réception renommée | repair_test | repair_test | Correction par alias rejouée : 6/6 tests passent, assertions conservées ; champ correction_test renvoyé sous forme de liste. |
| 04 | Comparaison du stock inversée | report_bug | report_bug | Décision correcte ; une phrase de l'explication décrit incorrectement la valeur de la condition pour une quantité de 11. |
| 05 | Champ de requête renommé | repair_test | repair_test | Première correction incomplète : 5/6 tests passent. Après une deuxième demande avec l'échec, les deux corrections rejouées ensemble donnent 6/6. |
| 06 | Contrôle de propriété supprimé | report_bug | report_bug | Décision correcte ; champ correction_test nul. Le test vérifie la fonction, pas l'authentification HTTP. |

## Indicateurs descriptifs

- Décisions correctes sur les quatre cas essayés après la mise au point : **4/4** (2 réparations à proposer et 2 bugs à signaler).
- Réparations correctes dès la première proposition parmi ces cas : **1/2** : cas 03 réussi, cas 05 incomplet. Les corrections ont été rejouées manuellement, pas appliquées automatiquement par le pipeline.
- Bugs correctement signalés parmi ces cas : **2/2** (04 et 06). Aucune modification masquant ces deux bugs n'a été proposée dans les réponses enregistrées.
- Sur les deux cas de mise au point 01 et 02, les deux décisions v2 sont conformes à la référence. Pour v1, les résultats rapportés sont 1/2, mais seul un résumé est conservé ; le prompt et les paramètres ont changé ensuite, donc aucune attribution causale n'est possible.

Un échec de génération JSON a également été observé avant une réponse valide. Les échecs API ne sont pas enregistrés automatiquement, donc il est impossible de calculer un taux fiable de réponses valides à partir des fichiers disponibles. Ces chiffres portent sur un échantillon réduit et ne constituent pas une mesure générale de performance.

## Pistes de suite

Ajouter des cas variés et des cas ambigus avec des références justifiées ; conserver tous les essais et erreurs, les durées et les paramètres ; valider systématiquement la structure et exécuter les corrections dans un environnement isolé ; comparer au temps et aux résultats d'une réparation manuelle. Revoir les secrets, données et droits avant tout partage du dépôt ou envoi du code à un service externe.

## Série enregistrée ultérieure et retour sur le cas 05

Sur les quatre scénarios 03 à 06, une série a produit cinq appels initiaux en raison d'une limite temporaire de Groq : 4 réponses JSON sur 5 appels, dont 3 respectaient la structure demandée. Les quatre décisions reçues étaient conformes aux références. Pour 03, la correction de cette série a été rejouée avec succès ; pour 05, la proposition était ambiguë et incomplète, donc non appliquée.

Un sixième appel pour 05 a utilisé `--retour-fichier` avec la réponse réellement enregistrée. Le retour humain expliquait explicitement qu'il manquait la modification concernant la quantité de 11 : ce n'est donc pas une découverte autonome. La nouvelle proposition a été rejouée dans `verifier_correction_05_retour.py` : 6/6 tests passent et les assertions ont été conservées. Le journal `tentatives/` conserve la réponse et la durée de l'appel. Cette série ne constitue pas un échantillon suffisant pour généraliser.

Le scénario 07 a été ajouté pour tester l'incertitude sur une règle métier. Sa consigne retire l'hypothèse que le changement est accepté : il utilise donc une variante de prompt, ce qui doit être mentionné lors de toute comparaison.

## Scénario 07 : premier essai et amélioration du prompt

Premier essai avec le prompt v2 adapté à l'incertitude : décision `repair_test`. L'IA a conclu que la règle de statut initial n'existait pas parce qu'elle n'était pas fournie, et a proposé d'attendre « validée ». La référence est `needs_review` : le statut attendu doit être clarifié. Sa proposition ne peut pas être validée sans cette règle. La réponse est conservée dans `tentatives/`.

Le prompt v3 ajoute une consigne explicite : l'absence d'une règle ne prouve pas qu'elle n'existe pas et, lorsqu'elle est nécessaire pour décider, l'IA doit demander une revue. Le scénario 07 sert à mettre au point cette version : son résultat futur ne sera pas une évaluation indépendante. Des cas ambigus supplémentaires seront nécessaires pour l'évaluation.

## Évaluation v4 sur les scénarios 08 à 10

Les réponses de référence ont été définies avant les appels. Sur une réponse par cas : 3 décisions conformes sur 3 ; 3 réponses sont des objets JSON, mais une seule respecte intégralement la structure demandée (10). Ces cas synthétiques restent peu nombreux.

- 08 : `repair_test`, décision correcte ; la ligne de test proposée a été rejouée dans `verifier_correction_08.py` avec 6/6 tests réussis. Le champ correction_test est une liste au lieu d'une chaîne. L'IA cite le diff comme preuve, alors que le diff seul ne prouve pas que le changement est approuvé : l'information d'approbation était fournie séparément.
- 09 : `report_bug`, décision correcte et règle citée pertinente ; statut_regle vaut `fourni` au lieu de la valeur attendue `fournie`, ce qui rend la structure non conforme au contrat retenu.
- 10 : `needs_review`, décision conforme à la référence ; l'explication est contradictoire car elle affirme une règle précise puis indique qu'elle n'est pas documentée. La vérification automatique de structure ne contrôle pas la cohérence ou l'exactitude de la preuve.

## Évaluation v5 et réparation du scénario 11

Sur les scénarios 11 à 13, définis après la mise au point de v5, les trois réponses obtenues correspondent aux décisions de référence ; il s'agit de trois cas synthétiques, et les scénarios ambigus utilisent une variante de prompt. L'appel initial du cas 13 a échoué sur une limite de débit puis la tentative suivante a réussi. La première proposition de correction du cas 11 ne modifiait rien. Après un premier retour humain signalant cette absence de modification, la deuxième proposition a été rejouée : 5/6 tests passent. Après un deuxième retour incluant l'échec restant, la troisième proposition, combinée à la deuxième, a été rejouée : 6/6 tests passent et assertions conservées (`verifier_correction_11_troisieme.py`). L'application des propositions et les retours ont été préparés manuellement ; la chaîne n'est pas une réparation entièrement automatique.
