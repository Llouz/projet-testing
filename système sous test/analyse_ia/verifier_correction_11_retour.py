"""Rejoue la proposition de la deuxième réponse du scénario 11."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

racine = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='verification_11_') as tmp:
    dossier = Path(tmp)
    shutil.copytree(racine / 'scenarios/11_champ_distributeur/version_initiale', dossier, dirs_exist_ok=True)
    code = dossier / 'backend/routes/pharmacie.py'
    source = code.read_text(encoding='utf-8')
    assert source.count('    distributeur_id: int\n') == 1 and source.count('data.distributeur_id') == 3
    code.write_text(source.replace('    distributeur_id: int\n', '    fournisseur_id: int\n').replace('data.distributeur_id', 'data.fournisseur_id'), encoding='utf-8')
    test = dossier / 'tests/test_commandes_pharmacie.py'
    source = test.read_text(encoding='utf-8')
    ancien = 'valeurs.update(changes)'
    nouveau = "valeurs.update({'fournisseur_id': valeurs.pop('distributeur_id'), **changes})"
    assert source.count(ancien) == 1
    nouveau_test = source.replace(ancien, nouveau)
    assert [x for x in source.splitlines() if 'assert ' in x] == [x for x in nouveau_test.splitlines() if 'assert ' in x]
    test.write_text(nouveau_test, encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(dossier)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=dossier, env=env)
    sys.exit(resultat.returncode)
