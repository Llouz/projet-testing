"""Vérifie la correction proposée pour le scénario 03 dans une copie temporaire."""
from pathlib import Path
import difflib
import os
import shutil
import subprocess
import sys
import tempfile

racine = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='verification_correction_03_') as tmp:
    copie = Path(tmp)
    shutil.copytree(racine / 'scenarios/03_renommage_reception/version_initiale', copie, dirs_exist_ok=True)
    code = copie / 'backend/routes/pharmacie.py'
    test = copie / 'tests/test_commandes_pharmacie.py'
    texte = code.read_text(encoding='utf-8')
    assert texte.count('def confirmer_reception(') == 1
    code.write_text(texte.replace('def confirmer_reception(', 'def enregistrer_reception('), encoding='utf-8')
    ancien = test.read_text(encoding='utf-8')
    avant = 'from backend.routes.pharmacie import CommandeRequest, commander, confirmer_reception'
    apres = 'from backend.routes.pharmacie import CommandeRequest, commander, enregistrer_reception as confirmer_reception'
    assert ancien.count(avant) == 1
    nouveau = ancien.replace(avant, apres)
    assert [x for x in ancien.splitlines() if 'assert ' in x] == [x for x in nouveau.splitlines() if 'assert ' in x]
    test.write_text(nouveau, encoding='utf-8')
    print(''.join(difflib.unified_diff(ancien.splitlines(keepends=True), nouveau.splitlines(keepends=True), fromfile='test_avant', tofile='test_corrige')), flush=True)
    env = os.environ.copy()
    env['PYTHONPATH'] = str(copie)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=copie, env=env)
    sys.exit(resultat.returncode)
