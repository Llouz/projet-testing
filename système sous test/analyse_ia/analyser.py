"""Prépare un cas et demande une analyse à Gemini, sans appliquer de modification."""
import argparse
import difflib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from controle_preuves import verifier_preuve
import urllib.error
import urllib.request

racine = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('cas', choices=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13'])
parser.add_argument('--preparer', action='store_true', help='Afficher le prompt sans appeler Gemini')
parser.add_argument('--fournisseur', choices=['gemini', 'groq'], default='gemini')
parser.add_argument('--modele', help='Nom du modèle (facultatif)')
parser.add_argument('--prompt', choices=['v1', 'v2', 'v3', 'v4', 'v5'], default='v2', help='Version du prompt')
parser.add_argument('--deuxieme-tentative', action='store_true', help='Rejouer la première correction du cas 05 et analyser son échec')
parser.add_argument('--retour-fichier', type=Path, help='Réponse enregistrée à analyser à nouveau (cas 05 ou 11)')
parser.add_argument('--troisieme-tentative-11', action='store_true', help='Rejouer la deuxième correction du scénario 11 avant analyse')
args = parser.parse_args()
if args.deuxieme_tentative and args.cas != '05':
    parser.error('--deuxieme-tentative est disponible uniquement pour le cas 05')
if args.retour_fichier and args.cas not in ('05', '11'):
    parser.error('--retour-fichier est disponible pour les cas 05 et 11')
if args.troisieme_tentative_11 and (args.cas != '11' or not args.retour_fichier):
    parser.error('--troisieme-tentative-11 exige le cas 11 et --retour-fichier')
if args.deuxieme_tentative and args.retour_fichier:
    parser.error('Choisir une seule méthode de retour')
nom = {'01': '01_renommage', '02': '02_bug_reception', '03': '03_renommage_reception', '04': '04_bug_stock', '05': '05_changement_donnee', '06': '06_bug_acces', '07': '07_statut_ambigu', '08': '08_changement_reponse', '09': '09_bug_stock_reception', '10': '10_quantite_ambigue', '11': '11_champ_distributeur', '12': '12_bug_confidentialite', '13': '13_limite_ambigue'}[args.cas]
source = racine / 'scenarios' / nom / 'version_initiale'
with tempfile.TemporaryDirectory(prefix='analyse_tests_') as temporaire:
    dossier = Path(temporaire)
    shutil.copytree(source, dossier, dirs_exist_ok=True)
    code_path = dossier / 'backend/routes/pharmacie.py'
    test_path = dossier / 'tests/test_commandes_pharmacie.py'
    ancien = code_path.read_text(encoding='utf-8')
    changements = {'01': ('def commander(', 'def passer_commande('), '02': ('commande.statut = "reçue"', 'commande.statut = "en_attente"'), '03': ('def confirmer_reception(', 'def enregistrer_reception('), '04': ('stock.quantite < data.quantite', 'stock.quantite > data.quantite')}
    changements['05'] = ('    quantite: int\n    distributeur_id: int', '    quantite_commandee: int\n    distributeur_id: int')
    changements['06'] = ('if not commande or commande.pharmacie_id != pharmacie_id:', 'if not commande:')
    changements['07'] = ('statut="en_attente"', 'statut="validée"')
    changements['08'] = ('return {"message": "Commande envoyée au distributeur", "commande": commande}', 'return {"confirmation": "Commande envoyée au distributeur", "commande": commande}')
    changements['09'] = ('stock.quantite += commande.quantite', 'stock.quantite -= commande.quantite')
    changements['10'] = ('stock.quantite += commande.quantite', 'stock.quantite += 2 * commande.quantite')
    changements['11'] = ('    distributeur_id: int\n', '    fournisseur_id: int\n')
    changements['12'] = ('return db.query(models.CommandePharmacie).filter_by(pharmacie_id=pharmacie_id).all()', 'return db.query(models.CommandePharmacie).all()')
    changements['13'] = ('stock.quantite < data.quantite', 'stock.quantite <= data.quantite')
    avant, apres = changements[args.cas]
    if ancien.count(avant) != 1:
        sys.exit('Le scénario ne correspond pas à sa version de référence.')
    nouveau = ancien.replace(avant, apres)
    if args.cas == '11':
        if nouveau.count('data.distributeur_id') != 3:
            sys.exit('Utilisations du distributeur inattendues.')
        nouveau = nouveau.replace('data.distributeur_id', 'data.fournisseur_id')
    if args.cas == '05':
        if nouveau.count('data.quantite') != 2:
            sys.exit('Utilisations de la quantité inattendues.')
        nouveau = nouveau.replace('data.quantite', 'data.quantite_commandee')
    code_path.write_text(nouveau, encoding='utf-8')
    if args.deuxieme_tentative:
        test_original = test_path.read_text(encoding='utf-8')
        ancien_test = "valeurs = {'medicament_id': 1, 'quantite': 3, 'distributeur_id': 2}"
        nouveau_test = "valeurs = {'medicament_id': 1, 'quantite_commandee': 3, 'distributeur_id': 2}"
        if test_original.count(ancien_test) != 1:
            sys.exit('La première correction ne correspond pas au test de référence.')
        test_path.write_text(test_original.replace(ancien_test, nouveau_test), encoding='utf-8')
    if args.troisieme_tentative_11:
        try:
            source_retour = json.loads(args.retour_fichier.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as erreur:
            sys.exit(f'Impossible de lire le résultat précédent : {erreur}')
        attendu = "valeurs.update(changes) -> valeurs.update({'fournisseur_id': valeurs.pop('distributeur_id'), **changes})"
        if source_retour.get('scenario') != '11' or source_retour.get('reponse', {}).get('correction_test') != attendu:
            sys.exit('Le fichier doit contenir la deuxième correction attendue pour le scénario 11.')
        test_original = test_path.read_text(encoding='utf-8')
        ancien_test = 'valeurs.update(changes)'
        nouveau_test = "valeurs.update({'fournisseur_id': valeurs.pop('distributeur_id'), **changes})"
        if test_original.count(ancien_test) != 1:
            sys.exit('La correction précédente ne correspond pas au test de référence.')
        test_path.write_text(test_original.replace(ancien_test, nouveau_test), encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(dossier)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=dossier, env=env, text=True, capture_output=True)
    if resultat.returncode not in (1, 2):
        sys.exit('Échec attendu non obtenu. Vérifiez l’environnement de test.')
    diff = ''.join(difflib.unified_diff(ancien.splitlines(keepends=True), nouveau.splitlines(keepends=True), fromfile='a/backend/routes/pharmacie.py', tofile='b/backend/routes/pharmacie.py'))
    code_pertinent = nouveau[nouveau.index('class CommandeRequest'):]
    prompt = f'''Analyse cet échec de test Python. Décide si le test est obsolète, si le code contient un bug, ou si une revue humaine est nécessaire. Ne modifie jamais une assertion uniquement pour faire passer le test. Préserve les règles métier. Retourne un objet JSON avec les champs decision (repair_test, report_bug ou needs_review), explication et correction_test (code ou null).

Règle métier : une commande validée dont la réception est confirmée passe au statut reçue et met à jour le stock. Une modification de nom d'une fonction ne change pas à elle seule son comportement.

Diff du code :\n{diff}\nCode concerné :\n{code_pertinent}\nTests :\n{test_path.read_text(encoding='utf-8')}\nRésultat pytest :\n{resultat.stdout}'''
    if args.cas == '11':
        prompt = prompt.replace('Diff du code :', 'Évolution d’interface approuvée : le champ de requête distributeur_id est renommé fournisseur_id ; le rôle et les autres règles restent inchangés.\n\nDiff du code :')
    if args.cas == '12':
        prompt = prompt.replace('Diff du code :', 'Règle métier supplémentaire : une pharmacie ne peut consulter que ses propres commandes.\n\nDiff du code :')
    if args.cas == '13':
        prompt = prompt.replace('Diff du code :', 'Règle métier supplémentaire : une pharmacie ne peut pas commander une quantité supérieure au stock disponible.\n\nDiff du code :')
    if args.cas == '08':
        prompt = prompt.replace('Diff du code :', 'Évolution d’interface approuvée : la réponse de création de commande utilise désormais la clé confirmation à la place de message ; le contenu textuel reste inchangé.\n\nDiff du code :')
    if args.cas == '09':
        prompt = prompt.replace('Diff du code :', 'Règle métier supplémentaire : la réception d’une commande augmente le stock existant de la pharmacie exactement de la quantité commandée.\n\nDiff du code :')
    if args.cas == '06':
        prompt = prompt.replace('Diff du code :', 'Règle métier supplémentaire : une pharmacie ne peut confirmer la réception d’une commande appartenant à une autre pharmacie.\n\nDiff du code :')
    if args.cas == '04':
        prompt = prompt.replace('Diff du code :', 'Règle métier supplémentaire : une commande ne doit pas être acceptée si la quantité demandée dépasse le stock du distributeur.\n\nDiff du code :')
    if args.prompt in ('v2', 'v3', 'v4', 'v5'):
        prompt = prompt.replace('Analyse cet échec de test Python.', '''Analyse cet échec de test Python.
Le diff décrit une évolution acceptée de l'interface, sauf si elle contredit une règle métier fournie. Ne suppose pas une obligation de conserver les anciens noms sans preuve. Si le comportement attendu reste respecté mais que le test appelle une ancienne interface, propose de réparer le test. Si le code contredit une règle métier, signale le bug et conserve le test. Si les éléments ne permettent pas de décider, demande une revue humaine.
Pour report_bug ou needs_review, correction_test doit être null. Pour repair_test, correction_test doit contenir uniquement les lignes à modifier dans le test, sans modifier le code de l'application. Réponds de façon concise.''')
    if args.cas in ('07', '10', '13') and args.prompt in ('v2', 'v3', 'v4', 'v5'):
        prompt = prompt.replace("Le diff décrit une évolution acceptée de l'interface, sauf si elle contredit une règle métier fournie.", "Le diff ne permet pas à lui seul de savoir si une évolution de comportement a été approuvée.")
    if args.prompt in ('v3', 'v4', 'v5'):
        prompt += '''

Une règle non fournie ne signifie pas qu'elle n'existe pas. Si une règle métier nécessaire pour déterminer si le changement de comportement est intentionnel manque, choisis needs_review, indique quelle règle doit être clarifiée et laisse correction_test à null. Ne déduis pas l'intention d'une modification uniquement du nouveau code.'''
    if args.prompt in ('v4', 'v5'):
        prompt += '''

Procède en deux étapes dans une seule réponse :
1. Indique la règle métier précise nécessaire à la décision dans regle_necessaire, puis cite dans preuve_regle le passage des règles fournies qui l'établit. Si ce passage n'existe pas, mets preuve_regle à null. Indique statut_regle : fournie ou manquante. Le code et les assertions ne suffisent pas à prouver qu'un nouveau comportement est approuvé.
2. Décide. Si la règle déterminante manque pour juger un changement de comportement, utilise needs_review et correction_test null ; pose la question à clarifier dans explication. Sinon, justifie repair_test ou report_bug à partir de la preuve.
Ajoute les trois champs regle_necessaire, preuve_regle, statut_regle à l'objet JSON demandé. Ne fournis pas de raisonnement caché ; une justification concise suffit.'''
    if args.prompt == 'v5':
        prompt += '''

Contrat JSON obligatoire : decision est exactement repair_test, report_bug ou needs_review ; explication et regle_necessaire sont des chaînes ; statut_regle est exactement fournie ou manquante. Si le statut est fournie, preuve_regle est une citation exacte, mot pour mot, d'une règle métier ou évolution d'interface fournie dans l'énoncé, sans guillemets supplémentaires. Ne cite pas le diff comme preuve de l'approbation. Si le statut est manquante, preuve_regle est null. Pour repair_test, correction_test est une seule chaîne contenant la correction et non une liste ; pour les autres décisions, correction_test est null. Vérifie la cohérence entre les champs et ne présente pas comme certaine une règle absente.'''
    if args.deuxieme_tentative:
        prompt += '''

Il s'agit d'une deuxième tentative. Une première proposition a déjà été appliquée : dans la fonction demande, le champ par défaut quantite a été remplacé par quantite_commandee. Le test ci-dessus contient cette proposition et le résultat pytest ci-dessus est celui obtenu après son application. Analyse l'échec restant et propose une correction complète des lignes de test concernées, sans changer les assertions ni le code applicatif.'''
    if args.retour_fichier:
        try:
            journal_source = json.loads(args.retour_fichier.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as erreur:
            sys.exit(f'Impossible de lire le résultat précédent : {erreur}')
        if journal_source.get('scenario') != args.cas or not isinstance(journal_source.get('reponse'), dict):
            sys.exit('Le fichier doit contenir une réponse enregistrée du scénario demandé.')
        reponse_precedente = json.dumps(journal_source['reponse'], ensure_ascii=False, indent=2)
        if args.cas == '05':
            retour = "Elle n'a pas été appliquée ni exécutée : son format est une liste de remplacements dont les lignes sont ambiguës, et elle ne précise pas la modification du paramètre quantite de valeur 11."
        elif args.troisieme_tentative_11:
            retour = "La correction précédente a été appliquée au test dans une copie isolée. Le test et les résultats pytest ci-dessus reflètent cet état : un échec subsiste."
        else:
            if journal_source['reponse'].get('correction_test') != 'valeurs.update(changes) -> valeurs.update(changes)':
                sys.exit('Ce retour attend la proposition sans modification enregistrée pour le scénario 11.')
            retour = "La correction précédente remplace une ligne par la même ligne et ne modifie donc pas le test. Les résultats pytest ci-dessus sont ceux de ce test inchangé après l’évolution du code."
        prompt += f'''\n\nVoici ta proposition précédente :\n{reponse_precedente}\n{retour} Repartez des tests ci-dessus et proposez une correction complète dans une seule chaîne correction_test. Indiquez précisément les portions à remplacer, sans changer les assertions ni le code applicatif.'''
    if args.preparer:
        print(prompt)
        sys.exit(0)
    variable = 'GROQ_API_KEY' if args.fournisseur == 'groq' else 'GEMINI_API_KEY'
    cle = os.environ.get(variable)
    if not cle:
        sys.exit(f'Clé absente : définissez {variable} dans ce terminal, puis relancez.')
    modele = args.modele or ('openai/gpt-oss-20b' if args.fournisseur == 'groq' else 'gemini-3.1-flash-lite')
    if not all(c.isalnum() or c in '-._/' for c in modele):
        sys.exit('Nom de modèle invalide.')
    if args.fournisseur == 'groq':
        url = 'https://api.groq.com/openai/v1/chat/completions'
        payload = {'model': modele, 'messages': [{'role': 'user', 'content': prompt}], 'response_format': {'type': 'json_object'}, 'max_completion_tokens': 8192}
        if modele.startswith('openai/gpt-oss-'):
            payload['reasoning_effort'] = 'low'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {cle}'}
    else:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent'
        payload = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json'}}
        headers = {'Content-Type': 'application/json', 'x-goog-api-key': cle}
    headers['User-Agent'] = 'projet-test-logiciel-etudiant/1.0'
    requete = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    journal = racine / 'analyse_ia' / 'tentatives'
    journal.mkdir(exist_ok=True)
    # Compteur propre à un scénario, fournisseur, modèle et version du prompt.
    # Il est indicatif si plusieurs instances sont lancées simultanément.
    numero = 1
    for chemin in journal.glob('*.json'):
        try:
            precedent = json.loads(chemin.read_text(encoding='utf-8'))
            if (precedent.get('scenario'), precedent.get('fournisseur'), precedent.get('modele'), precedent.get('version_prompt')) == (args.cas, args.fournisseur, modele, args.prompt):
                numero = max(numero, int(precedent.get('numero_tentative', 0)) + 1)
        except (OSError, ValueError, TypeError):
            continue
    debut = datetime.now(timezone.utc)
    depart = time.perf_counter()
    reponse_json = None
    erreur_info = None
    valide_json = False
    structure_valide = False
    try:
        with urllib.request.urlopen(requete, timeout=90) as reponse:
            data = json.load(reponse)
        if args.fournisseur == 'groq':
            texte = data['choices'][0]['message']['content']
        else:
            texte = ''.join(part.get('text', '') for part in data['candidates'][0]['content']['parts'])
        reponse_json = json.loads(texte)
        valide_json = isinstance(reponse_json, dict)
        if valide_json:
            decision = reponse_json.get('decision')
            correction = reponse_json.get('correction_test')
            structure_valide = (decision in ('repair_test', 'report_bug', 'needs_review')
                and isinstance(reponse_json.get('explication'), str)
                and 'correction_test' in reponse_json
                and ((decision == 'repair_test' and isinstance(correction, str))
                     or (decision in ('report_bug', 'needs_review') and correction is None)))
        if args.prompt in ('v4', 'v5') and structure_valide:
            preuve = reponse_json.get('preuve_regle')
            statut = reponse_json.get('statut_regle')
            structure_valide = (isinstance(reponse_json.get('regle_necessaire'), str)
                and statut in ('fournie', 'manquante')
                and ((statut == 'manquante' and preuve is None)
                     or (statut == 'fournie' and isinstance(preuve, str) and bool(preuve.strip()))))
        if not valide_json:
            erreur_info = {'type': 'json_non_objet', 'detail': 'La réponse JSON doit être un objet.'}
    except urllib.error.HTTPError as erreur:
        detail = erreur.read().decode('utf-8', errors='replace').replace(cle, '[CLE MASQUEE]')[:4000]
        erreur_info = {'type': 'http', 'code_http': erreur.code, 'detail': detail}
    except (urllib.error.URLError, TimeoutError, OSError) as erreur:
        erreur_info = {'type': 'connexion', 'detail': str(erreur).replace(cle, '[CLE MASQUEE]')[:1000]}
    except json.JSONDecodeError as erreur:
        erreur_info = {'type': 'json_invalide', 'detail': str(erreur).replace(cle, '[CLE MASQUEE]')[:1000]}
    except (KeyError, IndexError, TypeError) as erreur:
        erreur_info = {'type': 'reponse_api_inattendue', 'detail': str(erreur).replace(cle, '[CLE MASQUEE]')[:1000]}
    duree = round(time.perf_counter() - depart, 3)
    enregistrement = {
        'date_utc': debut.isoformat(), 'scenario': args.cas, 'version_prompt': args.prompt,
        'deuxieme_tentative': args.deuxieme_tentative, 'troisieme_tentative_11': args.troisieme_tentative_11, 'retour_fichier': str(args.retour_fichier) if args.retour_fichier else None, 'numero_tentative': numero,
        'fournisseur': args.fournisseur, 'modele': modele, 'duree_requete_secondes': duree,
        'json_objet_valide': valide_json, 'structure_valide': structure_valide,
        'prompt': prompt, 'reponse': reponse_json, 'erreur': erreur_info,
        'controle_preuve': verifier_preuve(prompt, reponse_json) if args.prompt in ('v4', 'v5') and valide_json else None,
    }
    horodatage = debut.strftime('%Y%m%dT%H%M%S%fZ')
    fichier = journal / f'{horodatage}_{args.cas}_{args.prompt}_{uuid.uuid4().hex[:8]}.json'
    contenu = json.dumps(enregistrement, ensure_ascii=False, indent=2).replace(cle, '[CLE MASQUEE]')
    fichier.write_text(contenu, encoding='utf-8')
    if erreur_info:
        print(f"Erreur API : {erreur_info['type']} — {erreur_info.get('detail', '')}", file=sys.stderr)
    else:
        print(json.dumps(reponse_json, ensure_ascii=False, indent=2).replace(cle, '[CLE MASQUEE]'))
        if not structure_valide:
            print('Attention : JSON reçu, mais structure attendue non respectée.')
    print(f'Tentative {numero} enregistrée : {fichier} (requête : {duree} s)')
    if erreur_info:
        sys.exit(1)
