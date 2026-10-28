# Analyse de tests assistée par IA

Ce dossier prépare des modifications de code dans une copie temporaire, lance pytest, et envoie le test, le code concerné, le diff et l'échec à Groq ou Gemini. Les réponses ne sont pas appliquées automatiquement. Consulter [BILAN.md](BILAN.md) et [journal_initial.md](journal_initial.md).

## Préparer l'environnement

Depuis la racine du projet sous Linux, créer un environnement virtuel et y installer les dépendances du backend et de test. Le fichier `backend/requirements.txt` est actuellement encodé en UTF-16 : la conversion ci-dessous en crée une copie temporaire en UTF-8, sans modifier l'original.

```bash
python3 -m venv .venv-tests
.venv-tests/bin/python -m pip install --upgrade pip
.venv-tests/bin/python -c "from pathlib import Path; Path('/tmp/projet-testing-backend-requirements.txt').write_text(Path('backend/requirements.txt').read_text(encoding='utf-16'), encoding='utf-8')"
.venv-tests/bin/python -m pip install -r /tmp/projet-testing-backend-requirements.txt -r requirements-tests.txt
.venv-tests/bin/python -m pytest tests/test_commandes_pharmacie.py tests/test_journal_tentatives.py -q
```

Installation vérifiée le 28 octobre 2026 dans un environnement virtuel neuf sous Linux avec Python 3.12 : les six tests principaux et la vérification de la deuxième correction du scénario 05 passent ; la préparation du scénario 06 fonctionne. L'installation n'a pas été vérifiée sur une autre machine ni sur un autre système d'exploitation. La version email-validator 2.1.0 du fichier backend est signalée comme retirée par PyPI mais a pu être installée dans cet essai. Sur la machine actuelle, l'environnement existant est `venv` : remplacer `.venv-tests/bin/python` par `venv/bin/python` si cet environnement est fonctionnel. SQLite est utilisé en mémoire, mais les dépendances nécessaires à l'import du backend restent requises.

## Analyser avec Groq

Créer une clé dans Groq, vérifier la formule et les quotas ; dans le terminal, sans partager ni enregistrer la clé dans le dépôt :

```bash
read -rs -p 'Clé Groq : ' GROQ_API_KEY; export GROQ_API_KEY; echo
.venv-tests/bin/python analyse_ia/analyser.py 03 --fournisseur groq --prompt v2
.venv-tests/bin/python analyse_ia/analyser.py 04 --fournisseur groq --prompt v2
```

Les numéros disponibles vont de 01 à 13. Pour les cas ambigus 07, 10 et 13, le prompt v2 retire l'hypothèse que l'évolution est acceptée ; il s'agit d'une variante du prompt. Par défaut, Groq utilise `openai/gpt-oss-20b` ; le modèle peut être modifié avec `--modele`. Pour préparer un prompt sans envoi réseau, ajouter `--preparer`. Pour reproduire la seconde demande du cas 05, ajouter `--deuxieme-tentative` à la commande du cas 05.

Les anciennes réponses réussies se trouvent dans `resultats/`. Les nouveaux appels à l'API, réussis ou non, sont enregistrés dans `tentatives/` avec date UTC, numéro de tentative, prompt, modèle, durée de la requête, réponse ou erreur, et indicateurs de validité JSON et de structure. La durée ne comprend pas la préparation des tests ni la revue humaine. Le numéro est compté par scénario, fournisseur, modèle et version du prompt ; il est indicatif si plusieurs appels sont lancés simultanément. Une tentative de correction complémentaire reste repérée par `deuxieme_tentative`. Le mode --preparer et les erreurs avant l'appel (par exemple clé absente) ne sont pas enregistrés comme appels API. L'historique antérieur n'est pas reconstitué. Ne jamais enregistrer de clé dans ces fichiers ; vérifier les données et les droits avant de transmettre du code à un fournisseur. Une autre exécution peut produire un résultat différent.

## Vérifier les réparations proposées

```bash
.venv-tests/bin/python analyse_ia/verifier_correction_01.py
.venv-tests/bin/python analyse_ia/verifier_correction_03.py
.venv-tests/bin/python analyse_ia/verifier_correction_05.py
.venv-tests/bin/python analyse_ia/verifier_correction_05_tentative2.py
```

Le troisième script doit échouer : il reproduit une correction incomplète. Le quatrième combine la première correction et celle proposée à la deuxième tentative. Ces scripts rejouent des modifications précises manuellement dans des copies temporaires ; ils ne valident pas automatiquement toute proposition future.

## Prompt v4

Le prompt v4 demande, dans un seul appel, d'identifier la règle nécessaire et sa preuve, puis de décider. Le journal vérifie la présence et le type de ces champs, mais ne vérifie pas que la preuve citée est exacte : une revue humaine reste nécessaire. Les scénarios utilisés pour ajuster le prompt ne sont pas une évaluation indépendante.

## Bilan automatique des nouveaux appels

```bash
venv/bin/python analyse_ia/bilan_tentatives.py --prompt v5 --cas 11 12 13
```

Le bilan lit uniquement `tentatives/` ; il ne reconstitue pas les anciens résultats dans `resultats/`. Il compte les erreurs HTTP parmi les appels, puis compare la première réponse JSON reçue par combinaison de scénario, fournisseur, modèle et version de prompt à la référence. Les retours sur une réponse précédente sont exclus de cette comparaison, mais restent inclus dans les nombres d'appels et durées. La durée moyenne porte sur les appels API mesurés, sans temps de préparation, d'attente entre essais ni revue humaine. La conformité de la décision ne prouve ni la qualité de la correction ni celle de la preuve ; les scénarios ambigus utilisent une variante de prompt.
