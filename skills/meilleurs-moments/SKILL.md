---
name: meilleurs-moments
description: Trouver les meilleurs moments à clipper dans une longue vidéo, une VOD de stream ou un fichier local. À utiliser quand l'utilisateur donne une URL YouTube ou Twitch ou un fichier vidéo et dit « trouve les moments », « les meilleurs passages », ou veut des candidats à découper.
---

# Meilleurs moments

Lance :

`$PY "${CLAUDE_PLUGIN_ROOT}/scripts/moments.py" <url-ou-fichier> --top 8`

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

Le script écrit `jobs/<id>/candidates.md`. Signaux utilisés : transcription avec horodatage par mot (faster-whisper), pics de volume, la courbe « les plus revus » de YouTube et les pics du chat en direct, quand ils existent. Un signal absent est ignoré, jamais simulé. Une VOD de plus de 90 minutes n'est analysée que sur les 90 premières (`--max-minutes` pour changer).

Ensuite :

1. Lis `jobs/<id>/candidates.md` et montre chaque candidat : numéro, début-fin, durée, pourquoi il a été retenu, phrase de la transcription.
2. Écarte les spoilers de l'histoire pendant la semaine de sortie, la nudité, et tout ce qui ressemble à une fuite.
3. Recommande les 3 meilleurs et dis quel angle d'accroche chacun suggère.
4. Étape suivante : `decoupe-clip` avec `--pick <n>`.

Note le lien source et le créateur dans les notes de `media/brut`. Crédite le créateur dans la légende du post (`🎥 @créateur`). En cas d'erreurs 403 de YouTube, *propose* `$PY -m pip install -U yt-dlp` et attends le oui.
