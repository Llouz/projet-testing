# Scénario 07 — Statut initial ambigu

Le code crée désormais une commande au statut « validée » au lieu de « en_attente ». Le test continue d'attendre « en_attente ». Aucune spécification fournie ne précise si la validation automatique à la création est une évolution autorisée ou un défaut.

Référence : `needs_review`. Il faut demander une clarification sur la règle du statut initial avant de modifier le test ou le code. L'évolution est artificielle et ne représente pas une modification approuvée du projet. Le prompt est adapté à ce cas : contrairement aux autres cas v2, il ne présente pas le changement comme accepté. La comparaison brute avec les résultats des autres prompts est donc limitée.
