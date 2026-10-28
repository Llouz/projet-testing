"""Prototype multi-agents : propositions et revue, sans application automatique."""
import argparse
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

RACINE = Path(__file__).resolve().parents[1]
ROLES = ('analyse', 'decision', 'verification')
INSTRUCTIONS = {
    'analyse': """Tu analyses un échec de test. Ne propose pas de correction finale. Fournis uniquement un objet JSON : changement (chaîne), comportement_teste (chaîne), regle_necessaire (chaîne), preuve_regle (citation exacte d'une règle fournie ou null), informations_manquantes (liste de chaînes). Ne suppose pas qu'une règle absente n'existe pas. Réponds de façon concise et renseigne tous les champs.""",
    'decision': """Classe l'échec selon la règle applicable, indépendamment de la solution envisagée :
- report_bug : une règle métier fournie est violée par le code ; expliquer le bug, sans correction de test.
- repair_test : une évolution d'interface explicitement approuvée rend le test obsolète sans contredire une règle métier ; proposer uniquement une correction du test, jamais du code applicatif.
- needs_review : la règle ou l'approbation nécessaire manque, ou les faits ne permettent pas de décider ; ne pas supposer la règle.
Réponds par JSON : decision, explication, preuve_decision (citation exacte d'une règle ou évolution approuvée, ou null si manquante), correction_test (chaîne si repair_test, sinon null), risques (liste de chaînes). Ne modifie pas les assertions pour dissimuler un défaut. Renseigne tous les champs et réponds de façon concise.""",
    'verification': """Tu vérifies de manière critique une proposition, à partir des faits originaux et de la décision proposée. Ne reçois aucune référence d'évaluation. Réponds par un objet JSON : avis (accept, reject ou needs_review), motifs (liste de chaînes), assertions_a_revoir (liste de chaînes), questions (liste de chaînes). Identifie les contradictions, les assertions affaiblies et les règles absentes. Ne prétends pas qu'une correction a été exécutée si aucun résultat d'exécution n'est fourni. Tous les champs JSON sont obligatoires : utilise [] pour les listes vides. Réponds de façon concise.""",
}


TEXTE = {'type': 'string'}
LISTE = {'type': 'array', 'items': {'type': 'string'}}
SCHEMAS = {
    'analyse': {'changement': TEXTE, 'comportement_teste': TEXTE, 'regle_necessaire': TEXTE, 'preuve_regle': {'type': ['string', 'null']}, 'informations_manquantes': LISTE},
    'decision': {'decision': {'type': 'string', 'enum': ['repair_test', 'report_bug', 'needs_review']}, 'explication': TEXTE, 'preuve_decision': {'type': ['string', 'null']}, 'correction_test': {'type': ['string', 'null']}, 'risques': LISTE},
    'verification': {'avis': {'type': 'string', 'enum': ['accept', 'reject', 'needs_review']}, 'motifs': LISTE, 'assertions_a_revoir': LISTE, 'questions': LISTE},
}


def format_reponse(role, modele):
    # Le schéma strict est utilisé uniquement pour les modèles explicitement pris en charge.
    if modele not in ('openai/gpt-oss-20b', 'openai/gpt-oss-120b'):
        return {'type': 'json_object'}
    proprietes = SCHEMAS[role]
    schema = {'type': 'object', 'properties': proprietes, 'required': list(proprietes), 'additionalProperties': False}
    return {'type': 'json_schema', 'json_schema': {'name': role, 'strict': True, 'schema': schema}}


def valider(role, obj):
    if not isinstance(obj, dict):
        raise ValueError('La réponse doit être un objet JSON.')
    liste = lambda x: isinstance(x, list) and all(isinstance(v, str) for v in x)
    if role == 'analyse':
        correct = all(isinstance(obj.get(k), str) for k in ('changement', 'comportement_teste', 'regle_necessaire')) and (obj.get('preuve_regle') is None or isinstance(obj.get('preuve_regle'), str)) and 'preuve_regle' in obj and liste(obj.get('informations_manquantes'))
    elif role == 'decision':
        decision = obj.get('decision')
        correction = obj.get('correction_test')
        correct = decision in ('repair_test', 'report_bug', 'needs_review') and isinstance(obj.get('explication'), str) and liste(obj.get('risques')) and 'preuve_decision' in obj and (obj['preuve_decision'] is None or isinstance(obj['preuve_decision'], str)) and 'correction_test' in obj and ((decision == 'repair_test' and isinstance(correction, str) and bool(correction.strip())) or (decision != 'repair_test' and correction is None))
    elif role == 'verification':
        correct = obj.get('avis') in ('accept', 'reject', 'needs_review') and all(liste(obj.get(k)) for k in ('motifs', 'assertions_a_revoir', 'questions'))
    else:
        raise ValueError('Rôle inconnu.')
    if not correct:
        raise ValueError(f'Format JSON invalide pour le rôle {role}.')


def preparer_faits(cas):
    cmd = [sys.executable, str(RACINE / 'analyse_ia/analyser.py'), cas, '--prompt', 'v5', '--preparer']
    res = subprocess.run(cmd, cwd=RACINE, text=True, capture_output=True)
    if res.returncode:
        raise RuntimeError('Préparation du scénario impossible : ' + (res.stderr or res.stdout)[-2000:])
    texte = res.stdout
    debut = texte.find('\nRègle métier :')
    fin = texte.find('\n\nUne règle non fournie', debut)
    if debut < 0 or fin < 0:
        raise RuntimeError('Format inattendu du scénario préparé.')
    return texte[debut:fin].strip()


def appeler_groq(prompt, modele, cle, role):
    url = 'https://api.groq.com/openai/v1/chat/completions'
    data = {'model': modele, 'messages': [{'role': 'user', 'content': prompt}], 'response_format': format_reponse(role, modele), 'max_completion_tokens': 2048}
    if modele.startswith('openai/gpt-oss-'):
        data['reasoning_effort'] = 'low'
    requete = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {cle}', 'User-Agent': 'projet-test-logiciel-multi-agent/1.0'})
    with urllib.request.urlopen(requete, timeout=90) as rep:
        donnees = json.load(rep)
    reponse = json.loads(donnees['choices'][0]['message']['content'])
    return reponse, donnees.get('usage')


def executer(cas, modele, cle, faits, appel=appeler_groq, attendre=time.sleep):
    journal = {'date_utc': datetime.now(timezone.utc).isoformat(), 'scenario': cas, 'modele': modele, 'fournisseur': 'groq', 'version_prompts': 'multi-v3', 'faits': faits, 'agents': [], 'statut': 'en_cours', 'decision_finale': None}
    sorties = {}
    for role in ROLES:
        message = INSTRUCTIONS[role] + '\n\nFAITS ORIGINAUX :\n' + faits
        if role == 'decision':
            message += '\n\nDIAGNOSTIC DE L’AGENT D’ANALYSE :\n' + json.dumps(sorties['analyse'], ensure_ascii=False)
        if role == 'verification':
            message += '\n\nPROPOSITION À VÉRIFIER :\n' + json.dumps(sorties['decision'], ensure_ascii=False)
        entree = {'role': role, 'prompt': message, 'reponse': None, 'usage': None, 'erreur': None, 'format_reponse': format_reponse(role, modele), 'tentatives': []}
        journal['agents'].append(entree)
        debut_total = time.perf_counter()
        for numero in range(1, 5):
            debut = time.perf_counter()
            essai = {'numero': numero, 'erreur': None, 'usage': None}
            entree['tentatives'].append(essai)
            try:
                reponse, usage = appel(message, modele, cle, role)
                entree['reponse'] = reponse
                entree['usage'] = usage
                essai['usage'] = usage
                valider(role, reponse)
                sorties[role] = reponse
            except urllib.error.HTTPError as erreur:
                detail = erreur.read().decode('utf-8', errors='replace')[:3000]
                essai['erreur'] = {'type': 'http', 'code': erreur.code, 'detail': detail}
            except (urllib.error.URLError, TimeoutError, OSError, ValueError, TypeError, KeyError, IndexError) as erreur:
                essai['erreur'] = {'type': type(erreur).__name__, 'detail': str(erreur)[:1000]}
            finally:
                essai['duree_appel_secondes'] = round(time.perf_counter() - debut, 3)
            if essai['erreur'] is None:
                entree['erreur'] = None
                break
            entree['erreur'] = essai['erreur']
            if numero == 4:
                break
            if essai['erreur'].get('code') == 400 and 'json_validate_failed' in essai['erreur'].get('detail', ''):
                print(f'Format incomplet pour {role} ; nouvelle tentative.', flush=True)
                continue
            if essai['erreur'].get('code') != 429:
                break
            correspondance = re.search(r'try again in\s+([0-9.]+)s', essai['erreur']['detail'], re.I)
            attente = float(correspondance.group(1)) + 0.5 if correspondance else 10.0
            if attente > 45:
                break
            essai['attente_avant_reprise_secondes'] = round(attente, 3)
            print(f'Quota atteint pour {role} ; nouvelle tentative dans {attente:.1f} s.', flush=True)
            attendre(attente)
        entree['duree_totale_secondes'] = round(time.perf_counter() - debut_total, 3)
        entree['duree_appel_secondes'] = round(sum(t['duree_appel_secondes'] for t in entree['tentatives']), 3)
        if entree['erreur']:
            journal['statut'] = 'erreur'
            return journal
    journal['statut'] = 'termine'
    preuve = sorties['decision'].get('preuve_decision')
    sources = [ligne.strip() for ligne in faits.splitlines() if ligne.startswith(('Règle métier :', 'Règle métier supplémentaire :', 'Évolution d’interface approuvée :'))]
    preuve_presente = bool(isinstance(preuve, str) and preuve.strip() and any(preuve.strip() in ligne for ligne in sources))
    journal['controle_preuve_decision'] = {'citation_presente': preuve_presente, 'note': 'Présence textuelle seulement ; pertinence et exactitude à vérifier humainement.'}
    avis = sorties['verification']['avis']
    proposee = sorties['decision']['decision']
    journal['decision_finale'] = {'decision_proposee': proposee, 'avis_verificateur': avis, 'decision_effective': proposee if avis == 'accept' and (proposee == 'needs_review' or preuve_presente) else 'needs_review', 'validation_humaine_requise': True}
    return journal


def main():
    parser = argparse.ArgumentParser(description='Prototype de trois rôles pour analyser un test en échec.')
    parser.add_argument('cas', choices=[f'{n:02d}' for n in range(1, 14)])
    parser.add_argument('--modele', default='openai/gpt-oss-20b')
    parser.add_argument('--preparer', action='store_true', help='Vérifier la préparation sans appeler Groq')
    args = parser.parse_args()
    try:
        faits = preparer_faits(args.cas)
    except (RuntimeError, OSError) as erreur:
        sys.exit(str(erreur))
    if args.preparer:
        print('Scénario préparé sans appel à l’API. Rôles : analyse, decision, verification.')
        print(f'{len(faits)} caractères de faits ; aucun résultat de référence transmis.')
        return
    cle = os.environ.get('GROQ_API_KEY')
    if not cle:
        sys.exit('Clé absente : définissez GROQ_API_KEY dans ce terminal.')
    journal = executer(args.cas, args.modele, cle, faits)
    repertoire = Path(__file__).resolve().parent / 'executions'
    repertoire.mkdir(exist_ok=True)
    fichier = repertoire / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{args.cas}_{uuid.uuid4().hex[:8]}.json"
    fichier.write_text(json.dumps(journal, ensure_ascii=False, indent=2).replace(cle, '[CLE MASQUEE]'), encoding='utf-8')
    for agent in journal['agents']:
        print(f"\n--- {agent['role']} ({agent['duree_appel_secondes']} s) ---")
        if agent['erreur']:
            print(json.dumps(agent['erreur'], ensure_ascii=False).replace(cle, '[CLE MASQUEE]'))
        else:
            print(json.dumps(agent['reponse'], ensure_ascii=False, indent=2).replace(cle, '[CLE MASQUEE]'))
    print(f'\nJournal : {fichier}')
    if journal['statut'] != 'termine':
        sys.exit(1)
    print('\nLa proposition n’a pas été appliquée ; une validation humaine reste nécessaire.')


if __name__ == '__main__':
    main()
