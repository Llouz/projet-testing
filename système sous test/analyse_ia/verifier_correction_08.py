"""Rejoue la correction proposée pour le scénario 08 dans une copie temporaire."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

racine = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='verification_08_') as tmp:
    copie = Path(tmp)
    shutil.copytree(racine / 'scenarios/08_changement_reponse/version_initiale', copie, dirs_exist_ok=True)
    code = copie / 'backend/routes/pharmacie.py'
    texte = code.read_text(encoding='utf-8')
    ancien = 'return {"message": "Commande envoyée au distributeur", "commande": commande}'
    nouveau = 'return {"confirmation": "Commande envoyée au distributeur", "commande": commande}'
    assert texte.count(ancien) == 1
    code.write_text(texte.replace(ancien, nouveau), encoding='utf-8')
    test = copie / 'tests/test_commandes_pharmacie.py'
    texte = test.read_text(encoding='utf-8')
    ancien = "assert resultat['message'] == 'Commande envoyée au distributeur'"
    nouveau = "assert resultat['confirmation'] == 'Commande envoyée au distributeur'"
    assert texte.count(ancien) == 1
    test.write_text(texte.replace(ancien, nouveau), encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(copie)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=copie, env=env)
    sys.exit(resultat.returncode)
