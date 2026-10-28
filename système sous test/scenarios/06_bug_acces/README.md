# Scénario 06 — Défaut de contrôle de propriété

Règle : une pharmacie ne peut confirmer la réception d'une commande appartenant à une autre pharmacie. Une modification supprime ce contrôle. Décision de référence : signaler le bug et conserver le test qui protège cette règle. Le test appelle directement la fonction avec un identifiant de pharmacie : il ne teste pas le mécanisme complet d'authentification HTTP.
