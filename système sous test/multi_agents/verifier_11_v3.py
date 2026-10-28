"""Rejoue la correction observée lors de l'essai multi-v3 du scénario 11."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

racine = Path(__file__).resolve().parents[1]
avec_avant = """def demande(**changes):
    valeurs = {'medicament_id': 1, 'quantite': 3, 'distributeur_id': 2}
    valeurs.update(changes)
    return CommandeRequest(**valeurs)"""
avec_apres = """def demande(**changes):
    valeurs = {'medicament_id': 1, 'quantite': 3, 'fournisseur_id': 2}
    valeurs.update(changes)
    return CommandeRequest(**valeurs)"""
with tempfile.TemporaryDirectory(prefix='multi_v3_verification_11_') as tmp:
    copie = Path(tmp)
    shutil.copytree(racine / 'scenarios/11_champ_distributeur/version_initiale', copie, dirs_exist_ok=True)
    code = copie / 'backend/routes/pharmacie.py'
    texte = code.read_text(encoding='utf-8')
    assert texte.count('    distributeur_id: int\n') == 1 and texte.count('data.distributeur_id') == 3
    code.write_text(texte.replace('    distributeur_id: int\n', '    fournisseur_id: int\n').replace('data.distributeur_id', 'data.fournisseur_id'), encoding='utf-8')
    test = copie / 'tests/test_commandes_pharmacie.py'
    texte = test.read_text(encoding='utf-8')
    assert texte.count(avec_avant) == 1
    apres = texte.replace(avec_avant, avec_apres)
    assert [x for x in texte.splitlines() if 'assert ' in x] == [x for x in apres.splitlines() if 'assert ' in x]
    test.write_text(apres, encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(copie)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=copie, env=env)
    sys.exit(resultat.returncode)
