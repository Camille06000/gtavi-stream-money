---
name: mode-live
description: Enregistrer un stream YouTube ou Twitch en direct avec son chat et clipper les pics du chat presque en temps réel. À utiliser quand l'utilisateur donne une URL de live, dit « mode live », « clippe le live », ou veut des clips d'un stream de sortie pendant qu'il se déroule.
---

# Mode live

Lance :

`$PY "${CLAUDE_PLUGIN_ROOT}/scripts/live.py" <url-du-live> --minutes 60`

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

URL YouTube live ou `https://twitch.tv/<pseudo>`. Le chat Twitch est lu sans clé (lecture seule, anonyme). Le script enregistre le stream par morceaux avec le chat et coupe autour de chaque pic du chat : 15 secondes avant et 20 secondes après. Les clips bruts arrivent dans `jobs/<id>/live/spike_<n>.mp4`, la liste dans `jobs/<id>/live/spikes.md`. Ctrl+C arrête plus tôt ; les pics en attente sont quand même coupés.

Avant de démarrer :

1. Vérifie que le stream est public et que ce n'est pas une fuite, une copie piratée ou du contenu « jouer en avance ». En cas de doute, ne démarre pas.
2. Note le pseudo du streamer pour le crédit.

Pendant l'enregistrement :

1. Regarde les nouveaux clips dans `jobs/<id>/live/` toutes les quelques minutes. Passe chacun en revue : garde le meilleur, écarte spoilers et nudité.
2. Pour chaque clip retenu : `meilleurs-moments` sur le fichier `spike_<n>.mp4` (`--top 1`), puis `accroches`, `decoupe-clip`, puis `verif-regles`.
3. Envoie à l'utilisateur un seul message avec les 1 à 3 meilleurs clips (légende, crédit, chemin du fichier). La vitesse compte : un seul message.

À la fin : liste ce qui a été enregistré et ce qui a été clippé, et note les posts publiés par l'utilisateur via `suivi-resultats`. Si le streamer est joignable, prépare un brouillon de message pour lui demander l'autorisation ; l'utilisateur l'envoie lui-même.

**Règle absolue : Claude prépare, l'utilisateur publie.** Montre les fichiers et la légende, puis attends un « oui » explicite de l'utilisateur pour chaque clip. Ne publie, ne programme et n'envoie jamais rien toi-même, même si un outil de publication est connecté.
