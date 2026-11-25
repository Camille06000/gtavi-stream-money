---
name: suivi-resultats
description: Noter les posts et apprendre des vrais chiffres avec scores.csv, apprentissages.md et gains.csv. À utiliser après la publication d'un post, aux relevés de 12/24/72 heures, pour le bilan du soir ou de la semaine, ou quand l'utilisateur demande « qu'est-ce qui marche », « fais le bilan », « combien j'ai gagné ».
---

# Suivi des résultats

Fichiers du dossier de la page : `scores.csv` (une ligne par post, colonnes en anglais), `apprentissages.md` (Victoires, Échecs, Règles actuelles), `gains.csv` (montants réels uniquement), `journal.md`.

## Règles

1. Vrais chiffres uniquement. Demande à l'utilisateur de coller ses statistiques ou une capture d'écran. Si un chiffre n'est pas disponible, laisse la case vide. Ne devine jamais.
2. Note chaque post quand l'utilisateur l'a publié : post_id, date, time, platform, pillar, format, hook, length_sec, credit, test_name.
3. Les relevés à 12 h, 24 h et 72 h remplissent views_12h, views_24h, views_72h, puis likes, reposts_or_shares, replies_or_comments, saves_or_bookmarks, followers_at_read.
4. Un test par jour. Ne change qu'une variable (style d'accroche, durée, heure de publication, longueur de légende, image fixe ou clip). Nomme-le dans `test_name`.
5. Aucun verdict avant 24 heures. Préfère le relevé à 72 h si le post bouge encore.
6. `gains.csv` : n'enregistre que ce que la campagne ou la plateforme affiche réellement. Ne projette jamais de gains. Commandes (depuis le dossier de la page) :
   - `$PY "${CLAUDE_PLUGIN_ROOT}/scripts/payouts.py" add --platform tiktok --post-url URL --views 12000 --rate-per-1k 0.5 --campaign NOM` (vues et tarif tels que la campagne les affiche ; statut `pending` par défaut)
   - `$PY "${CLAUDE_PLUGIN_ROOT}/scripts/payouts.py" report` (totaux par campagne ; `est_payout` est une estimation, pas un gain confirmé)

   `$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

## Chaque soir

Meilleur et pire post, une leçon écrite sous forme de règle. Ajoute-la à `apprentissages.md`. Choisis le test de demain.

## Chaque semaine

Top 3 et flop 3, vues médianes par pilier, par créneau horaire et par plateforme. Insiste sur ce qui est au-dessus de la médiane. Retravaille ou abandonne ce qui est resté sous la médiane toute la semaine. Choisis les tests de la semaine suivante. Mets à jour `guide.md` avec ce qui a changé. Envoie à l'utilisateur un court résumé.

Relevés tard le soir : dis ce qui manque encore au lieu de le remplir.

Ce skill ne publie rien : Claude prépare, l'utilisateur publie.
