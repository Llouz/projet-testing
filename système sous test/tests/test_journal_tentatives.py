"""Vérification locale du journal sans appel externe."""
import io
import json
import runpy
import shutil
import sys
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import urlopen
from unittest.mock import patch

import pytest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def executer(tmp_path, monkeypatch, reponse=None, erreur=None):
    dossier = tmp_path / 'projet'
    (dossier / 'analyse_ia').mkdir(parents=True)
    shutil.copy(ROOT / 'analyse_ia/analyser.py', dossier / 'analyse_ia/analyser.py')
    shutil.copy(ROOT / 'analyse_ia/controle_preuves.py', dossier / 'analyse_ia/controle_preuves.py')
    monkeypatch.syspath_prepend(str(dossier / 'analyse_ia'))
    shutil.copytree(ROOT / 'scenarios/01_renommage/version_initiale', dossier / 'scenarios/01_renommage/version_initiale')
    monkeypatch.setenv('GROQ_API_KEY', 'cle-secrete-fictive')
    monkeypatch.setattr(sys, 'argv', ['analyser.py', '01', '--fournisseur', 'groq'])
    sortie = SimpleNamespace(returncode=1, stdout='Échec fictif')
    with patch('subprocess.run', return_value=sortie), patch('urllib.request.urlopen', side_effect=erreur, return_value=reponse):
        try:
            runpy.run_path(str(dossier / 'analyse_ia/analyser.py'), run_name='__main__')
            code = 0
        except SystemExit as exc:
            code = exc.code
    fichiers = list((dossier / 'analyse_ia/tentatives').glob('*.json'))
    assert len(fichiers) == 1
    texte = fichiers[0].read_text(encoding='utf-8')
    assert 'cle-secrete-fictive' not in texte
    return code, json.loads(texte)


def simuler(message):
    contenu = json.dumps({'choices': [{'message': {'content': message}}]}).encode()
    return io.BytesIO(contenu)


def test_reponse_valide(tmp_path, monkeypatch):
    code, journal = executer(tmp_path, monkeypatch, simuler('{"decision":"report_bug","explication":"Bug","correction_test":null}'))
    assert code == 0
    assert journal['json_objet_valide'] and journal['structure_valide']
    assert journal['erreur'] is None and journal['numero_tentative'] == 1
    assert journal['duree_requete_secondes'] >= 0


def test_json_malforme(tmp_path, monkeypatch):
    code, journal = executer(tmp_path, monkeypatch, simuler('{invalid'))
    assert code == 1
    assert journal['erreur']['type'] == 'json_invalide'
    assert not journal['json_objet_valide']


def test_structure_non_conforme(tmp_path, monkeypatch):
    code, journal = executer(tmp_path, monkeypatch, simuler('{"decision":"repair_test","explication":"ok","correction_test":["x"]}'))
    assert code == 0
    assert journal['json_objet_valide'] and not journal['structure_valide']


def test_erreur_http_masque_cle(tmp_path, monkeypatch):
    erreur = HTTPError('https://exemple.invalid', 403, 'Forbidden', {}, io.BytesIO(b'cle-secrete-fictive interdit'))
    code, journal = executer(tmp_path, monkeypatch, erreur=erreur)
    assert code == 1
    assert journal['erreur']['code_http'] == 403
    assert '[CLE MASQUEE]' in journal['erreur']['detail']


def test_controle_preuve_verifie_uniquement_les_regles():
    import importlib.util
    module_path = ROOT / 'analyse_ia/controle_preuves.py'
    spec = importlib.util.spec_from_file_location('controle_preuves_test', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prompt = 'Règle métier supplémentaire : le stock augmente.\n\nDiff du code :\n+ le stock augmente.'
    assert module.verifier_preuve(prompt, {'preuve_regle': 'le stock augmente.'})['citation_presente'] is True
    assert module.verifier_preuve(prompt, {'preuve_regle': 'Diff du code'})['citation_presente'] is False
    assert module.verifier_preuve(prompt, {'preuve_regle': None})['citation_presente'] is None
