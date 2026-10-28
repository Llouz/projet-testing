"""Contrôle du calcul des indicateurs sans appel réseau."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('bilan_tentatives', Path(__file__).resolve().parents[1] / 'analyse_ia/bilan_tentatives.py')
bilan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bilan)


def test_premiere_reponse_et_erreurs_et_retours():
    base = {'scenario': '11', 'fournisseur': 'groq', 'modele': 'test', 'version_prompt': 'v5'}
    donnees = [
        {**base, 'date_utc': '01', 'erreur': {'type': 'http'}, 'json_objet_valide': False, 'duree_requete_secondes': 1},
        {**base, 'date_utc': '02', 'erreur': None, 'json_objet_valide': True, 'structure_valide': True, 'reponse': {'decision': 'repair_test'}, 'duree_requete_secondes': 3},
        {**base, 'date_utc': '03', 'erreur': None, 'json_objet_valide': True, 'structure_valide': True, 'retour_fichier': 'fichier', 'reponse': {'decision': 'report_bug'}, 'duree_requete_secondes': 2},
    ]
    r = bilan.resumer(donnees)
    assert (r['nombre_appels'], r['objets_json'], r['structures_valides']) == (3, 2, 2)
    assert (r['decisions_correctes'], r['premieres_reponses']) == (1, 1)
    assert r['erreurs'] == {'http': 1}
    assert r['duree_moyenne_secondes'] == 2
