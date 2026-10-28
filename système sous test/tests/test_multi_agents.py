"""Tests locaux du prototype, sans appel réel au modèle."""
from pathlib import Path
import importlib.util

import pytest

fichier = Path(__file__).resolve().parents[1] / 'multi_agents/orchestrateur.py'
spec = importlib.util.spec_from_file_location('orchestrateur_test', fichier)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def reponses():
    return [
        {'changement': 'renommage', 'comportement_teste': 'création', 'regle_necessaire': 'nom', 'preuve_regle': None, 'informations_manquantes': []},
        {'decision': 'repair_test', 'explication': 'champ renommé', 'preuve_decision': None, 'correction_test': 'modifier le champ', 'risques': []},
        {'avis': 'needs_review', 'motifs': ['vérifier la correction'], 'assertions_a_revoir': [], 'questions': []},
    ]


def test_flux_complet():
    valeurs = iter(reponses())
    prompts = []
    def appel(prompt, modele, cle, role):
        prompts.append(prompt)
        return next(valeurs), {'total_tokens': 10}
    result = module.executer('11', 'test', 'cle-fictive', 'faits synthétiques', appel=appel)
    assert result['statut'] == 'termine'
    assert [x['role'] for x in result['agents']] == list(module.ROLES)
    assert result['decision_finale']['validation_humaine_requise'] is True
    assert result['decision_finale']['avis_verificateur'] == 'needs_review'
    assert result['decision_finale']['decision_effective'] == 'needs_review'
    assert 'DIAGNOSTIC' in prompts[1] and 'PROPOSITION À VÉRIFIER' in prompts[2]
    assert 'DIAGNOSTIC DE L’AGENT' not in prompts[2]


def test_format_invalide_arrete_flux():
    def appel(prompt, modele, cle, role):
        return {'changement': 'insuffisant'}, None
    result = module.executer('11', 'test', 'cle-fictive', 'faits', appel=appel)
    assert result['statut'] == 'erreur'
    assert len(result['agents']) == 1
    assert result['agents'][0]['erreur']['type'] == 'ValueError'
    assert result['decision_finale'] is None


def test_reponse_bug_ne_contient_pas_correction():
    with pytest.raises(ValueError):
        module.valider('decision', {'decision': 'report_bug', 'explication': 'bug', 'preuve_decision': 'règle', 'correction_test': 'modifier test', 'risques': []})


def test_preparation_scenario_sans_reference():
    faits = module.preparer_faits('11')
    assert 'Diff du code :' in faits and 'Résultat pytest :' in faits
    assert 'réponse de référence' not in faits.lower()
    assert 'Contrat JSON obligatoire' not in faits


def test_schema_strict_selon_le_role():
    for role in module.ROLES:
        format_ = module.format_reponse(role, 'openai/gpt-oss-20b')
        schema = format_['json_schema']['schema']
        assert format_['json_schema']['strict'] is True
        assert schema['additionalProperties'] is False
        assert set(schema['required']) == set(schema['properties'])
    assert module.format_reponse('analyse', 'autre-modele') == {'type': 'json_object'}


def test_quota_avec_reprise():
    import io
    from urllib.error import HTTPError
    valeurs = iter(reponses())
    appels = []
    attentes = []
    def appel(prompt, modele, cle, role):
        appels.append(role)
        if len(appels) == 1:
            raise HTTPError('https://exemple.invalid', 429, 'quota', {}, io.BytesIO(b'Please try again in 2.5s'))
        return next(valeurs), None
    resultat = module.executer('11', 'test', 'cle', 'faits', appel=appel, attendre=attentes.append)
    assert resultat['statut'] == 'termine'
    assert len(resultat['agents'][0]['tentatives']) == 2
    assert resultat['agents'][0]['tentatives'][0]['erreur']['code'] == 429
    assert attentes == [3.0]


def test_json_refuse_une_nouvelle_tentative():
    import io
    from urllib.error import HTTPError
    valeurs = iter(reponses())
    appels = []
    def appel(prompt, modele, cle, role):
        appels.append(role)
        if len(appels) == 1:
            raise HTTPError('https://exemple.invalid', 400, 'bad', {}, io.BytesIO(b'{"code":"json_validate_failed"}'))
        return next(valeurs), None
    resultat = module.executer('11', 'test', 'cle', 'faits', appel=appel, attendre=lambda _: None)
    assert resultat['statut'] == 'termine'
    assert len(resultat['agents'][0]['tentatives']) == 2
    assert resultat['agents'][0]['tentatives'][0]['erreur']['code'] == 400


def test_preuve_absente_force_la_revue():
    donnees = reponses()
    donnees[2]['avis'] = 'accept'
    valeurs = iter(donnees)
    resultat = module.executer('11', 'test', 'cle', 'Règle métier : exemple', appel=lambda *_: (next(valeurs), None))
    assert resultat['statut'] == 'termine'
    assert resultat['controle_preuve_decision']['citation_presente'] is False
    assert resultat['decision_finale']['decision_effective'] == 'needs_review'


def test_citation_presente_ne_remplace_pas_revision_humaine():
    donnees = reponses()
    donnees[1]['preuve_decision'] = 'règle explicite'
    donnees[2]['avis'] = 'accept'
    valeurs = iter(donnees)
    resultat = module.executer('11', 'test', 'cle', 'Règle métier : règle explicite', appel=lambda *_: (next(valeurs), None))
    assert resultat['controle_preuve_decision']['citation_presente'] is True
    assert resultat['decision_finale']['decision_effective'] == 'repair_test'
    assert resultat['decision_finale']['validation_humaine_requise'] is True
