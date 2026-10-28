"""Rejoue une évolution et sa réparation dans un dossier temporaire."""
from pathlib import Path
import difflib
import os
import shutil
import subprocess
import sys
import tempfile

scenario = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='scenario_commandes_') as tmp:
    copie = Path(tmp)
    shutil.copytree(scenario / 'version_initiale', copie, dirs_exist_ok=True)
    code = copie / 'backend/routes/pharmacie.py'
    test = copie / 'tests/test_commandes_pharmacie.py'
    env = os.environ.copy()
    env['PYTHONPATH'] = str(copie)

    def executer(etape, attendu):
        print(f'\n--- {etape} ---', flush=True)
        resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=copie, env=env)
        if (resultat.returncode == 0) != attendu:
            raise SystemExit(f'Resultat inattendu : code {resultat.returncode}')

    executer('1. Version initiale : tests attendus en réussite', True)
    ancien = code.read_text(encoding='utf-8')
    assert ancien.count('def commander(') == 1
    nouveau = ancien.replace('def commander(', 'def passer_commande(')
    code.write_text(nouveau, encoding='utf-8')
    print('\nDiff de l’évolution :', flush=True)
    print(''.join(difflib.unified_diff(ancien.splitlines(keepends=True), nouveau.splitlines(keepends=True), fromfile='a/backend/routes/pharmacie.py', tofile='b/backend/routes/pharmacie.py')), flush=True)
    executer('2. Après évolution : échec attendu', False)
    ancien_test = test.read_text(encoding='utf-8')
    assert 'import CommandeRequest, commander, confirmer_reception' in ancien_test
    nouveau_test = ancien_test.replace('import CommandeRequest, commander, confirmer_reception', 'import CommandeRequest, passer_commande, confirmer_reception').replace('commander(demande(', 'passer_commande(demande(')
    test.write_text(nouveau_test, encoding='utf-8')
    print('\nDiff de la réparation de référence :', flush=True)
    print(''.join(difflib.unified_diff(ancien_test.splitlines(keepends=True), nouveau_test.splitlines(keepends=True), fromfile='a/tests/test_commandes_pharmacie.py', tofile='b/tests/test_commandes_pharmacie.py')), flush=True)
    executer('3. Après réparation : tests attendus en réussite', True)
