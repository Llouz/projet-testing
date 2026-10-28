"""Rejoue manuellement la proposition de l'IA dans une copie temporaire."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

racine = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='verification_correction_05_') as tmp:
    copie = Path(tmp)
    shutil.copytree(racine / 'scenarios/05_changement_donnee/version_initiale', copie, dirs_exist_ok=True)
    code = copie / 'backend/routes/pharmacie.py'
    test = copie / 'tests/test_commandes_pharmacie.py'
    texte = code.read_text(encoding='utf-8')
    assert texte.count('    quantite: int\n    distributeur_id: int') == 1 and texte.count('data.quantite') == 2
    code.write_text(texte.replace('    quantite: int\n    distributeur_id: int', '    quantite_commandee: int\n    distributeur_id: int').replace('data.quantite', 'data.quantite_commandee'), encoding='utf-8')
    texte = test.read_text(encoding='utf-8')
    ancien = "valeurs = {'medicament_id': 1, 'quantite': 3, 'distributeur_id': 2}"
    nouveau = "valeurs = {'medicament_id': 1, 'quantite_commandee': 3, 'distributeur_id': 2}"
    assert texte.count(ancien) == 1
    test.write_text(texte.replace(ancien, nouveau), encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(copie)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=copie, env=env)
    sys.exit(resultat.returncode)
