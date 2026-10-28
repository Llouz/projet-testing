"""Rejoue la proposition du retour 05, sans modifier le projet actif."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='verif_retour_05_') as tmp:
    dossier = Path(tmp)
    shutil.copytree(root / 'scenarios/05_changement_donnee/version_initiale', dossier, dirs_exist_ok=True)
    code = dossier / 'backend/routes/pharmacie.py'
    contenu = code.read_text(encoding='utf-8')
    assert contenu.count('    quantite: int\n    distributeur_id: int') == 1 and contenu.count('data.quantite') == 2
    code.write_text(contenu.replace('    quantite: int\n    distributeur_id: int', '    quantite_commandee: int\n    distributeur_id: int').replace('data.quantite', 'data.quantite_commandee'), encoding='utf-8')
    fichier = dossier / 'tests/test_commandes_pharmacie.py'
    original = fichier.read_text(encoding='utf-8')
    avant = """def demande(**changes):
    valeurs = {'medicament_id': 1, 'quantite': 3, 'distributeur_id': 2}
    valeurs.update(changes)
    return CommandeRequest(**valeurs)"""
    apres = """def demande(**changes):
    # Le champ quantite a été renommé en quantite_commandee
    valeurs = {'medicament_id': 1, 'quantite_commandee': 3, 'distributeur_id': 2}
    # Mettre à jour avec les modifications éventuelles (ex : quantite -> quantite_commandee)
    # On doit aussi gérer le cas où la modification se fait sur la quantité
    if 'quantite' in changes:
        valeurs['quantite_commandee'] = changes.pop('quantite')
    valeurs.update(changes)
    return CommandeRequest(**valeurs)"""
    assert original.count(avant) == 1
    corrige = original.replace(avant, apres)
    assert [x for x in original.splitlines() if 'assert ' in x] == [x for x in corrige.splitlines() if 'assert ' in x]
    fichier.write_text(corrige, encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(dossier)
    resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=dossier, env=env)
    sys.exit(resultat.returncode)
