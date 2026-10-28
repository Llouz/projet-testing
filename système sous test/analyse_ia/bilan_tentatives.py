"""Bilan descriptif des appels enregistrés, sans juger automatiquement les réparations."""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics

REFERENCES = {
    '01': 'repair_test', '02': 'report_bug', '03': 'repair_test',
    '04': 'report_bug', '05': 'repair_test', '06': 'report_bug',
    '07': 'needs_review', '08': 'repair_test', '09': 'report_bug',
    '10': 'needs_review', '11': 'repair_test', '12': 'report_bug',
    '13': 'needs_review',
}


def resumer(donnees):
    appels = [d for d in donnees if isinstance(d, dict)]
    succes = [d for d in appels if d.get('erreur') is None and d.get('json_objet_valide') is True]
    resultats = {}
    # Un groupe est un scénario, fournisseur, modèle et version de prompt.
    # Les retours sur une proposition antérieure ne sont pas des premiers essais.
    for d in sorted(succes, key=lambda x: x.get('date_utc', '')):
        if d.get('retour_fichier') or d.get('deuxieme_tentative') or d.get('troisieme_tentative_11'):
            continue
        cle = (d.get('scenario'), d.get('fournisseur'), d.get('modele'), d.get('version_prompt'))
        resultats.setdefault(cle, d)
    juges = [(cle, d) for cle, d in resultats.items() if cle[0] in REFERENCES and isinstance(d.get('reponse'), dict)]
    corrects = sum(d['reponse'].get('decision') == REFERENCES[cle[0]] for cle, d in juges)
    durees = [d['duree_requete_secondes'] for d in appels if isinstance(d.get('duree_requete_secondes'), (int, float)) and not isinstance(d.get('duree_requete_secondes'), bool)]
    return {'nombre_appels': len(appels), 'objets_json': len(succes),
            'structures_valides': sum(d.get('structure_valide') is True for d in appels),
            'erreurs': dict(Counter((d.get('erreur') or {}).get('type', 'inconnue') for d in appels if isinstance(d.get('erreur'), dict))),
            'premieres_reponses': len(juges), 'decisions_correctes': corrects,
            'duree_moyenne_secondes': round(statistics.mean(durees), 3) if durees else None,
            'durees_mesurees': len(durees), 'groupes': len(resultats)}


def main():
    parser = argparse.ArgumentParser(description='Résumer les tentatives enregistrées dans le projet.')
    parser.add_argument('--prompt', choices=['v1', 'v2', 'v3', 'v4', 'v5'])
    parser.add_argument('--cas', nargs='+', choices=list(REFERENCES))
    parser.add_argument('--modele')
    args = parser.parse_args()
    dossier = Path(__file__).resolve().parent / 'tentatives'
    donnees = []
    erreurs_lecture = 0
    for fichier in sorted(dossier.glob('*.json')):
        try:
            entree = json.loads(fichier.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            erreurs_lecture += 1
            continue
        if not isinstance(entree, dict):
            erreurs_lecture += 1
            continue
        if args.prompt and entree.get('version_prompt') != args.prompt:
            continue
        if args.cas and entree.get('scenario') not in args.cas:
            continue
        if args.modele and entree.get('modele') != args.modele:
            continue
        donnees.append(entree)
    bilan = resumer(donnees)
    print(f"Appels : {bilan['nombre_appels']}")
    print(f"Réponses JSON objet : {bilan['objets_json']}/{bilan['nombre_appels']}")
    print(f"Structures conformes : {bilan['structures_valides']}/{bilan['nombre_appels']}")
    print(f"Erreurs API : {bilan['erreurs'] or 'aucune'}")
    print(f"Décisions conformes parmi les premières réponses : {bilan['decisions_correctes']}/{bilan['premieres_reponses']}")
    print(f"Durée moyenne des appels mesurés : {bilan['duree_moyenne_secondes']} s ({bilan['durees_mesurees']} appels)")
    print(f"Fichiers illisibles ignorés : {erreurs_lecture}")
    print('Durées : appels API uniquement. Les premières réponses excluent les retours ; les refus API sont comptés dans les appels.')
    print('La conformité de la décision ne vérifie ni la preuve, ni la correction : une revue et des tests restent nécessaires.')


if __name__ == '__main__':
    main()
