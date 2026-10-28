# Journal des premiers essais

Ces réponses ont été recopiées depuis les résultats communiqués dans la conversation. Les horodatages exacts et les prompts complets envoyés ne sont pas disponibles dans l'historique d'exécution ; ne pas les présenter comme enregistrés automatiquement. Fournisseur : Groq ; modèle utilisé par défaut : openai/gpt-oss-20b ; version du prompt : v1. Une seule réponse par scénario.

## Scénario 01 : renommage

Décision : `report_bug`. Explication : le test importe `commander`, renommée `passer_commande` ; l'IA propose un alias de compatibilité. Champ correction_test : `commander = passer_commande`. Décision attendue dans notre scénario : `repair_test`, sous l'hypothèse que le renommage est une évolution acceptée. Résultat : décision différente de la référence ; l'hypothèse de compatibilité de l'IA n'était pas explicitement exclue par le premier prompt.

## Scénario 02 : statut de réception

Décision : `report_bug`. L'IA explique que la commande devrait passer à « reçue » après confirmation et signale la contradiction du code. Elle fournit dans correction_test une version corrigée de la fonction applicative, alors que le champ désigne une correction de test. Décision attendue : `report_bug`. Résultat : décision correcte, mais contenu du champ mal adapté.

## Comparaison à réaliser

Le prompt v2 précise l'hypothèse sur les changements d'interface et impose un champ correction_test nul lorsque le test ne doit pas être réparé. Les nouveaux essais sont enregistrés automatiquement dans resultats, avec les prompts et les réponses. Comparer même modèle et mêmes scénarios. Ces deux scénarios ont servi à concevoir le prompt : ils ne sont pas un jeu d'évaluation indépendant.
