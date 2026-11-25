---
name: tendances
description: Classer les vidéos GTA 6 récentes par vues par heure pour voir ce qui monte en ce moment. À utiliser quand l'utilisateur demande « qu'est-ce qui marche », « quoi clipper aujourd'hui », « quoi poster aujourd'hui », les tendances, ou des vidéos sources fraîches.
---

# Tendances

Lance :

`$PY "${CLAUDE_PLUGIN_ROOT}/scripts/trends.py" --query "gta 6" --hours 24 --limit 30`

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page. Le résultat complet est écrit dans `tendances.md`.

Change `--query` pour d'autres angles (« gta 6 map », « gta 6 trailer », « gta 6 fr », un pseudo de streamer). Change `--hours` pour une fenêtre plus large.

Ensuite :

1. Montre le top 10 dans un petit tableau : titre, chaîne, vues, vues par heure, âge, lien.
2. Choisis-en 3 qui collent à l'angle de la page. Préfère les sources officielles et les créateurs qui autorisent le partage.
3. Signale celles qui ressemblent à des fuites ou à du « jouer en avance » : écarte-les et dis-le.
4. Propose l'étape suivante pour les choix : `meilleurs-moments <url> --top 8`.

Si le script plante, montre la dernière ligne d'erreur et corrige la cause (venv ou yt-dlp manquant : relance `installation` ; réseau). En cas d'erreurs 403 de YouTube, *propose* `$PY -m pip install -U yt-dlp` et attends le oui. N'invente jamais de liste.
