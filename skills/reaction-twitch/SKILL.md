---
name: reaction-twitch
description: "Suivre un gros streamer GTA 6 sur Twitch et faire des clips de réaction : visage en haut, jeu en bas, gros titre. À utiliser quand l'utilisateur veut des clips de réaction de streamer, des clips « visage en haut », des clips Twitch, ou demande qui stream GTA 6 en ce moment."
---

# Clips de réaction Twitch

Visage en haut, jeu en bas, un gros titre sur la jonction. Le format de la plupart des clips de streamers GTA 6 qui deviennent viraux.

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

## 1. Trouver le streamer

- Avec les clés Twitch dans `.env` : `$PY "${CLAUDE_PLUGIN_ROOT}/scripts/streams.py" --query "gta 6"` liste les streams GTA 6 en direct sur Twitch (API officielle Helix) et YouTube, classés par spectateurs (`--lang fr` pour les streams Twitch en français).
- Sans clés : Twitch est ignoré par ce script. Demande à l'utilisateur le pseudo du streamer.

Choisis un streamer qui a une campagne de clipping ouverte (vérifie `campagnes.md`) ou dont tu as l'autorisation de publier les clips. Un streamer FR (Squeezie, Domingo…) seulement si sa campagne est ouverte ou avec son accord.

## 2. Récupérer le moment

- En direct : `$PY "${CLAUDE_PLUGIN_ROOT}/scripts/live.py" https://twitch.tv/<pseudo> --minutes 60` enregistre le stream, lit le chat Twitch de façon anonyme (sans clé) et coupe un clip à chaque explosion du chat.
- Après coup : `$PY "${CLAUDE_PLUGIN_ROOT}/scripts/moments.py" <URL de VOD ou de clip Twitch> --top 8` note la VOD et écrit `candidates.md`.

## 3. Découper le clip de réaction

Le streamer parle anglais ? C'est le format phare d'une page francophone : le moment le plus fou d'un gros live américain, sous-titré en français. Traduis toi-même les sous-titres, c'est bien meilleur que la traduction automatique sur l'argot :

1. `$PY "${CLAUDE_PLUGIN_ROOT}/scripts/cut.py" jobs/<id> --pick 1 --export-sentences` écrit `jobs/<id>/edits/clip_1_phrases.txt` (une phrase par ligne).
2. Écris `jobs/<id>/edits/clip_1_fr.txt` : une ligne traduite par phrase, même ordre, même nombre de lignes. Français naturel et oral (« bro » → « frérot »), rien d'ajouté, rien d'inventé ; si la transcription est confuse, reste au plus près du sens. Les injures sont masquées ensuite par le script.
3. Découpe :

```
$PY "${CLAUDE_PLUGIN_ROOT}/scripts/cut.py" jobs/<id> --pick 1 --layout react --cam auto \
  --title "<Pseudo> a CRAQUÉ quand les FLICS sont arrivés dans GTA 6" --title-style box --captions word \
  --translations jobs/<id>/edits/clip_1_fr.txt
```

- `--translate fr` à la place de `--translations` : traduction automatique (Google, une requête par clip). Solution de secours, à relire.
- Le streamer est détouré sur fond vert, sans cadre de webcam ? `--cam auto` refusera : passe le cadrage à la main avec `--cam x:y:w:h` (fractions de l'image, ex. `0.005:0.30:0.17:0.23` pour un streamer en bas à gauche) et vérifie une image.

- `--cam auto` trouve seul la webcam du streamer (détection du visage et du cadre de la webcam autour). Il affiche où il l'a trouvée. S'il ne trouve pas de visage au-dessus du jeu, ou pas de jeu hors de la webcam, il s'arrête avec `skipped` : choisis un autre moment. Vérifie la première image une fois ; si le cadrage est faux, passe `--cam x:y:w:h` en fractions.
- `--title-style box` : bande blanche avec texte noir en gras sur la jonction. `--title-style outline` : texte blanc avec un épais contour noir en haut du jeu, pour les titres courts (« Face aux flics dans GTA 6 »).
- `--captions bubble` : bulle blanche avec la phrase dite. `word` : sous-titres mot à mot. `none` : titre seul.
- Écris le titre avec `accroches` (section titres de réaction).

## Règles

- Ne clippe un streamer que dans le cadre de sa campagne ou avec son autorisation. Crédite-le dans la légende du post (`🎥 @créateur`), pas sur la vidéo.
- Les titres décrivent ce qui s'est passé. N'invente jamais une citation ni une opinion.
- Lance `verif-regles` avant de publier. Pas de spoiler dans le titre pendant la semaine de sortie.

**Règle absolue : Claude prépare, l'utilisateur publie.** Montre le fichier et la légende, puis attends un « oui » explicite de l'utilisateur. Ne publie, ne programme et n'envoie jamais rien toi-même.
