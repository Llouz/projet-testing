"""Démonstration d'un bug et d'une fausse réparation dans une copie temporaire."""
from pathlib import Path
import difflib
import os
import shutil
import subprocess
import sys
import tempfile

scenario = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='scenario_bug_') as tmp:
    copie = Path(tmp)
    shutil.copytree(scenario / 'version_initiale', copie, dirs_exist_ok=True)
    code = copie / 'backend/routes/pharmacie.py'
    test = copie / 'tests/test_commandes_pharmacie.py'
    env = os.environ.copy()
    env['PYTHONPATH'] = str(copie)

    def executer(titre, code_attendu, texte_attendu=None):
        print(f'\n--- {titre} ---', flush=True)
        resultat = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_commandes_pharmacie.py', '-q', '--disable-warnings'], cwd=copie, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(resultat.stdout, flush=True)
        if resultat.returncode != code_attendu or (texte_attendu and texte_attendu not in resultat.stdout):
            raise SystemExit('Résultat inattendu : vérifier les dépendances et la version de référence.')

    def afficher_diff(ancien, nouveau, chemin):
        print(''.join(difflib.unified_diff(ancien.splitlines(keepends=True), nouveau.splitlines(keepends=True), fromfile='a/' + chemin, tofile='b/' + chemin)), flush=True)

    executer('1. Version initiale', 0, '6 passed')
    ancien = code.read_text(encoding='utf-8')
    assert ancien.count('commande.statut = "reçue"') == 1
    bug = ancien.replace('commande.statut = "reçue"', 'commande.statut = "en_attente"')
    code.write_text(bug, encoding='utf-8')
    print('\nModification volontaire qui introduit le bug :', flush=True)
    afficher_diff(ancien, bug, 'backend/routes/pharmacie.py')
    executer('2. Le test détecte le bug', 1, 'test_reception_ajoute_au_stock_existant')
    ancien_test = test.read_text(encoding='utf-8')
    assert ancien_test.count("assert commande.statut == 'reçue'") == 1
    faux_test = ancien_test.replace("assert commande.statut == 'reçue'", "assert commande.statut == 'en_attente'")
    test.write_text(faux_test, encoding='utf-8')
    print('\nFausse réparation : elle modifie la règle attendue et masque le bug.', flush=True)
    afficher_diff(ancien_test, faux_test, 'tests/test_commandes_pharmacie.py')
    executer('3. Les tests passent malgré le bug', 0, '6 passed')
    print('\nConclusion attendue : signaler le bug, ne pas accepter cette modification du test.', flush=True)
