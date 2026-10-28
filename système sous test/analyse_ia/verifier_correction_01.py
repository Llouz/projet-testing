"""Rejoue la correction de l'essai v2 dans une copie sans exécuter de code arbitraire de l'IA."""
from pathlib import Path
import difflib
import os
import shutil
import subprocess
import sys
import tempfile

racine = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='verification_correction_') as tmp:
    copie = Path(tmp)
    shutil.copytree(racine / 'scenarios/01_renommage/version_initiale', copie, dirs_exist_ok=True)
    code = copie / 'backend/routes/pharmacie.py'
    test = copie / 'tests/test_commandes_pharmacie.py'
    code_texte = code.read_text(encoding='utf-8')
    assert code_texte.count('def commander(') == 1
    code.write_text(code_texte.replace('def commander(', 'def passer_commande('), encoding='utf-8')
    ancien = test.read_text(encoding='utf-8')
    origine = 'from backend.routes.pharmacie import CommandeRequest, commander, confirmer_reception'
    remplacement = 'from backend.routes.pharmacie import CommandeRequest, passer_commande as commander, confirmer_reception'
    assert ancien.count(origine) == 1
    nouveau = ancien.replace(origine, remplacement)
    assert [x for x in ancien.splitlines() if 'assert ' in x] == [x for x in nouveau.splitlines() if 'assert ' in x]
    test.write_text(nouveau, encoding='utf-8')
    print('Diff de la correction proposée par l’IA :', flush=True)
    print(''.join(difflib.unified_diff(ancien.splitlines(keepends=True), nouveau.splitlines(keepends=True), fromfile='test_avant', tofile='test_corrige')), flush=True)
    env = os.environ.copy()
    env['PYTHONPATH'] = str(copie)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=copie, env=env)
    sys.exit(resultat.returncode)
