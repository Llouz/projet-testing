# Guide de démonstration — Sujet 3

## Avant la présentation

Vérifier la connexion et les quotas Groq, préparer la clé dans le terminal sans l'afficher, et tester les commandes. Prévoir les résultats déjà enregistrés en cas d'indisponibilité réseau. Ne jamais montrer ou publier la clé. Les sorties d'API peuvent varier entre exécutions.

Depuis le répertoire `système sous test` :

```bash
venv/bin/python -m pytest tests/test_commandes_pharmacie.py -q --disable-warnings
venv/bin/python analyse_ia/bilan_tentatives.py --prompt v5 --cas 11 12 13
```

Pour configurer la clé au besoin :

```bash
read -rs -p 'Clé Groq : ' GROQ_API_KEY; export GROQ_API_KEY; echo
```

## Déroulement suggéré (8 à 10 minutes)

1. **Problème et objectif (1 min).** Expliquer qu'un test en échec peut être obsolète, révéler un bug ou nécessiter une clarification. Le risque étudié est de masquer un bug en changeant le test.
2. **Architecture (1 min).** Montrer les composants : application FastAPI, tests pytest avec SQLite en mémoire, diff produit par Python, prompt avec règles métier, API Groq, réponse JSON et journal. Les corrections sont aujourd'hui revues et rejouées manuellement.
3. **Évolution de code — scénario 01 (2 min).** Lancer la démonstration locale :

   ```bash
   venv/bin/python scenarios/01_renommage/demo.py
   ```

   Expliquer : avant, les six tests passent ; après renommage, l'import du test échoue ; après correction de référence écrite manuellement, les six tests passent. Ce script ne fait pas d'appel IA.

4. **Vrai bug — scénario 02 (2 min).** Lancer :

   ```bash
   venv/bin/python scenarios/02_bug_reception/demo.py
   ```

   Montrer qu'un test détecte le statut erroné, puis qu'une fausse correction du test peut faire passer la suite tout en masquant le défaut. La bonne décision est de signaler le bug. La fausse correction est volontaire et n'affecte qu'une copie temporaire.

5. **Essai IA (1–2 min).** Si le réseau est disponible, appeler par exemple :

   ```bash
   venv/bin/python analyse_ia/analyser.py 12 --fournisseur groq --prompt v5
   ```

   Lire la décision et la règle citée, en expliquant que l'appel envoie le code et les tests au fournisseur. Vérifier la réponse au lieu de supposer que le modèle sera toujours correct. En cas d'erreur ou de limite, ouvrir une réponse enregistrée dans `analyse_ia/tentatives/`.

6. **Résultats et limites (1–2 min).** Afficher le bilan v5 des cas 11 à 13. Expliquer les 3 décisions correctes sur 3 premières réponses reçues, l'erreur HTTP parmi les 6 appels et le scénario 11 réparé seulement après deux retours. Signaler que la durée n'inclut pas la revue humaine et que les cas sont synthétiques et peu nombreux.

## Questions à anticiper

- Pourquoi un test qui passe ne suffit-il pas ? Une assertion peut être affaiblie et masquer un bug.
- La réparation est-elle automatique ? L'analyse et le journal le sont ; l'application et la vérification des propositions actuelles sont préparées manuellement.
- Comment sont traitées les règles manquantes ? Un cas ambigu attend une revue humaine ; l'IA peut néanmoins se tromper.
- Les résultats prouvent-ils l'efficacité générale ? Non : l'échantillon est réduit et les scénarios sont construits pour l'étude.
- Quels coûts ? Quotas et temps d'appel sont observés ; les coûts et le temps humain complets restent à mesurer selon le fournisseur et la formule.
