---
name: streams-live
description: Trouver les streams GTA 6 en direct sur YouTube (et Twitch si les clés sont configurées), classés par spectateurs. À utiliser quand l'utilisateur demande « qui stream en ce moment », « trouve un live », veut des moments en direct à clipper, ou avant `mode-live`.
---

# Streams live

Lance :

`$PY "${CLAUDE_PLUGIN_ROOT}/scripts/streams.py" --query "gta 6"`

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page. Le résultat est écrit dans `streams.md`, une section par plateforme.

- YouTube marche toujours, sans clé.
- Pour des streams francophones : `--lang fr` filtre Twitch ; sur YouTube, ajoute « fr » à `--query`.
- Twitch (catégorie Grand Theft Auto VI) passe par l'API officielle Helix et n'apparaît que si `TWITCH_CLIENT_ID` et `TWITCH_CLIENT_SECRET` sont dans le `.env` du dossier de la page (ou en variables d'environnement). Sans clés, Twitch est ignoré : dis-le en une ligne et rappelle comment les obtenir (application gratuite sur https://dev.twitch.tv/console ; l'utilisateur écrit lui-même ses clés dans `.env`, ne lui demande jamais de les coller dans le chat).

Ensuite :

1. Montre le top 10 des streams en direct : plateforme, chaîne, titre, spectateurs, lien.
2. Écarte les streams qui sont clairement des fuites, des astuces d'accès anticipé ou des copies piratées. Dis pourquoi en une ligne.
3. Recommande 1 à 3 streams. Préfère les chaînes officielles et les créateurs qui autorisent le partage (vérifie `campagnes.md`).
4. Propose l'étape suivante : `mode-live <url> --minutes 60` pour enregistrer et clipper les pics du chat, ou `meilleurs-moments` sur une VOD terminée.

Les nombres de spectateurs sont ceux que le script renvoie à cet instant. Ne les devine pas et ne les arrondis pas vers le haut. En cas d'erreurs 403 de YouTube, *propose* `$PY -m pip install -U yt-dlp` et attends le oui.
