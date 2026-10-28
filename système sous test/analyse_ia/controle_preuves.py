"""Contrôles formels des preuves ; aucun jugement automatique de pertinence."""

def textes_de_reference(prompt):
    prefixes = ('Règle métier :', 'Règle métier supplémentaire :', 'Évolution d’interface approuvée :')
    return [ligne.strip() for ligne in prompt.splitlines() if ligne.startswith(prefixes)]


def verifier_preuve(prompt, reponse):
    if not isinstance(reponse, dict):
        return {'citation_presente': None, 'commentaire': 'Réponse non structurée.'}
    preuve = reponse.get('preuve_regle')
    if preuve is None:
        return {'citation_presente': None, 'commentaire': 'Pas de citation ; vérifier manuellement si la règle est absente.'}
    if not isinstance(preuve, str) or not preuve.strip():
        return {'citation_presente': False, 'commentaire': 'Citation absente ou de type invalide.'}
    presente = any(preuve.strip() in texte for texte in textes_de_reference(prompt))
    return {'citation_presente': presente, 'commentaire': 'Vérifie uniquement la présence textuelle dans les règles et évolutions fournies, pas la pertinence ni la vérité de la preuve.'}
