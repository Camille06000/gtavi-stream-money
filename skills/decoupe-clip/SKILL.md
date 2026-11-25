---
name: decoupe-clip
description: Transformer un moment choisi en clip vertical 1080x1920 fini, avec sous-titres mot à mot et encadré d'accroche. À utiliser après `meilleurs-moments`, ou quand l'utilisateur dit « découpe le clip », « fais le clip », « mets-le en vertical ».
---

# Découpe clip

Lance :

`$PY "${CLAUDE_PLUGIN_ROOT}/scripts/cut.py" jobs/<id> --pick <n> --layout fill|blur|facecam --hook "TEXTE"`

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

- `fill` : recadre la vidéo du jeu pour remplir l'image. Choix par défaut pour du gameplay.
- `blur` : vidéo entière centrée sur une copie floutée. Quand le recadrage couperait l'action.
- `facecam` : gameplay avec la caméra du streamer. Pour les réactions (pour le format visage en haut et gros titre, voir `reaction-twitch`).
- Streamer anglophone : sous-titres en français. De préférence traduits par toi : `--export-sentences` écrit `edits/clip_<n>_phrases.txt`, tu écris `edits/clip_<n>_fr.txt` (une ligne par phrase, même ordre, rien d'inventé), puis tu relances avec `--translations edits/clip_<n>_fr.txt`. Secours : `--translate fr` (traduction automatique, à relire). La mise en page est conservée, réaction comprise.

Avant de lancer :

1. Demande 3 accroches au skill `accroches` et prends la meilleure.

Après :

1. Le fichier sort dans `jobs/<id>/edits/clip_<n>.mp4` (avec `clip_<n>.json`, lu par `verif-regles` et `multilangue`). Vérifie qu'il fait 1080x1920, que l'accroche apparaît dans les 2 premières secondes et que les sous-titres sont lisibles. Aucun crédit n'est incrusté dans la vidéo : le crédit va dans la légende du post (`🎥 @créateur`).
2. Lance `verif-regles` dessus. Corrige et redécoupe jusqu'à ce qu'il passe. Une fois validé, copie-le dans `media/montages`.
3. 7 à 30 secondes pour la plupart des clips (ajuste avec `--start` et `--end`, en secondes dans la source). Termine sur le moment fort.

**Règle absolue : Claude prépare, l'utilisateur publie.** Montre à l'utilisateur le fichier et le texte de la légende, puis attends un « oui » explicite. N'uploade et ne publie rien toi-même.
