---
name: pilote-auto
description: Pilote automatique de la page. Regarde un gros live GTA 6 anglophone sur Twitch ou YouTube, découpe ses meilleurs moments en clips réaction sous-titrés en français, les vérifie, les publie par les API officielles (YouTube Shorts, Instagram Reels, TikTok) puis passe au live suivant. À utiliser quand une tâche planifiée lance « pilote-auto », ou quand l'utilisateur dit « lance le pilote automatique », « fais un passage du pilote ».
---

# Pilote automatique

Ce skill tourne sans personne devant l'écran. L'utilisateur l'a activé lui-même dans `pilote.json` : c'est la seule exception à la règle « Claude prépare, l'utilisateur publie », et elle ne couvre que ce qui est écrit ici.

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. `S` = `${CLAUDE_PLUGIN_ROOT}/scripts`. Lance tout depuis le dossier de la page.

## 0. Avant tout

1. Va dans le dossier de la page (celui qui contient `pilote.json`). S'il manque, arrête-toi : rien d'autre à faire.
2. Un fichier `PAUSE` dans le dossier ? Arrête-toi sans rien faire.
3. Lis `pilote.json` :
   - `mode` : `test` (rien n'est publié) ou `auto` (publication réelle). Seul l'utilisateur change ce mode. Ne le modifie jamais.
   - `plateformes`, `max_par_jour`, `minutes_de_live`, `clips_par_passage`, `streamers_prioritaires`, `twitch_prioritaires`, `exclus`, `fuseau`.
4. `$PY "S/publish.py" today` : si le plafond est atteint sur toutes les plateformes, note-le dans `journal.md` et arrête-toi.
5. Un clip attend dans `a-publier/` (un `.mp4` et son `.json` avec `titre` et `description`) ? Publie-le d'abord (étape 4), puis retire-le du dossier.
6. Le lundi seulement : `$PY "S/publish.py" auth instagram` renouvelle le jeton Instagram (il expire au bout de 60 jours).

## 1. Choisir le live

Twitch passe en premier quand c'est possible : son chat se lit en direct (IRC), donc les pics du chat y marchent.

1. **Twitch avec clés** (`TWITCH_CLIENT_ID` et `TWITCH_CLIENT_SECRET` dans `.env`) : `$PY "S/streams.py" --query "gta 6" --lang en --out streams.md` liste YouTube et les lives Twitch anglophones de GTA 6 (API officielle).
2. **Twitch sans clés** : pour chaque pseudo de `twitch_prioritaires`, `$PY "S/live.py" https://www.twitch.tv/<pseudo> --apercu`. « impossible d'obtenir l'adresse du flux » veut dire hors ligne ; sinon regarde l'aperçu (étape 6). Sans clés, Twitch ne donne ni le jeu ni le nombre de spectateurs : seule l'image fait foi.
   Puis, pour YouTube : `$PY "S/streams.py" --query "gta 6" --out streams.md`.
3. Garde les lives **en anglais** qui montrent vraiment GTA 6. Priorité aux `streamers_prioritaires` et `twitch_prioritaires`, à Twitch plutôt qu'à YouTube, puis au plus grand nombre de spectateurs.
4. Écarte : les chaînes de `exclus` et de `retraits.md`, les fuites, « play early », le piratage, l'argent ou les bots de GTA Online.
5. Ne reprends pas la chaîne du passage précédent (dernière ligne de `registre.csv`), sauf si c'est la seule.
6. **Vérifie l'image avant d'enregistrer** : `$PY "S/live.py" <url> --apercu` écrit `jobs/<id>/live/apercu.jpg`. Regarde-la. Un titre qui dit « GTA 6 » ne suffit pas : si l'écran montre un autre jeu, un écran d'attente ou un menu, passe au live suivant.
7. Aucun live valable : note-le dans `journal.md` et arrête-toi.

## 2. Regarder

`$PY "S/live.py" <url> --minutes <minutes_de_live> --baseline 120`

La commande dure le temps du live demandé. Elle écrit `jobs/<id>/live/spike_<n>.mp4` à chaque pic du chat, `spikes.md`, et à la fin `jobs/<id>/live/enregistrement.mp4` (tout l'enregistrement recollé).

## 3. Choisir et découper (au plus `clips_par_passage` clips)

Les sources, dans l'ordre :
- les pics du chat (`spike_<n>.mp4`), du plus fort au plus faible (colonne msgs de `spikes.md`) ;
- s'il n'y a aucun pic (le chat YouTube n'est pas toujours lisible) : `enregistrement.mp4`, avec `--top 3` à l'étape 1.

Pour chaque source :

1. `$PY "S/moments.py" <source> --top 1 --min 12 --max 35` crée un nouveau job (`--top 3` pour `enregistrement.mp4`).
2. Lis son `candidates.md`, puis regarde une image de chaque moment (`ffmpeg -ss <début+5> -i <source> -frames:v 1 <job>/moment_<n>.jpg`). Écarte : autre jeu que GTA 6, cinématique de l'histoire pendant la semaine de sortie (spoiler), nudité, propos haineux, moment sans le jeu à l'écran, tout ce qui ressemble à une fuite.
3. **Qualité minimum.** Garde le moment seulement s'il a une action visible (poursuite, crash, fusillade, cascade) ou une réaction claire et drôle du streamer. Un pic du chat ne suffit pas : regarde 5 ou 6 images autour du pic. Transcription quasi vide ou inaudible et rien de marquant à l'image : écarte. Mieux vaut aucun clip qu'un clip plat.
4. Déjà dans `registre.csv` (même chaîne, même moment) ? Passe au suivant.
5. Recadre sur la réaction : lis `transcript.json` (mots horodatés) et choisis `--start` / `--end` (en secondes dans la source) pour garder la phrase du streamer et couper les dialogues de l'histoire. Garde au moins 12 secondes.
6. Sous-titres français, traduits par toi : `cut.py <job> --pick <n> [--start S --end E] --export-sentences`, puis écris `edits/clip_<n>_fr.txt` (une ligne par phrase, même ordre, français oral, rien d'inventé).
7. Titre de réaction écrit selon `accroches` : il décrit ce qui s'est passé, sans citation inventée, sans spoiler.
8. `cut.py <job> --pick <n> [--start S --end E] --layout react --cam auto --title "<titre>" --captions word --translations <job>/edits/clip_<n>_fr.txt`. Refusé faute de webcam en cadre ? Recommence avec `--layout blur`.
9. `check.py <clip> --caption "<légende>"` doit finir par `RÉSULTAT : OK`. Sinon, le clip est abandonné.
10. Chaque moment écarté va aussi dans `registre.csv` (statut « écarté : raison »), pour ne pas le réexaminer au passage suivant.

## 4. Publier

Légende : l'accroche en français, « Sous-titré en français », `🎥 @<chaîne>`, puis 3 à 5 hashtags (`#GTA6 #GTAVI` + le streamer). Description : la même, plus le lien du live d'origine.

- `mode` = `test` : `$PY "S/publish.py" post <clip> --title "<légende>" --description "<description>" --platforms <plateformes séparées par des virgules> --max-per-day <max_par_jour> --youtube-privacy <youtube_visibilite> --test`
- `mode` = `auto` : la même commande sans `--test`. Elle passe par les API officielles (YouTube Data API, Instagram Graph API, TikTok Content Posting API). Une plateforme pas encore connectée reste automatiquement en test.
- Un seul clip publié par passage. Le second clip retenu va dans `a-publier/` (copie le `.mp4` et écris à côté un `.json` avec `titre` et `description`) : il partira au début du passage suivant.

`publish.py` refuse sans crédit et au-delà du plafond : ne le contourne jamais. Un statut « en ligne privée » veut dire que l'appli YouTube ou TikTok n'est pas encore auditée : note-le dans `journal.md`, c'est normal.
Ajoute une ligne à `registre.csv` (crée-le avec l'en-tête `date,chaine,url,moment,fichier,mode,statut` s'il n'existe pas).

## 5. Fin de passage

Ajoute à `journal.md` : l'heure, le live regardé, le nombre de pics, et une ligne par clip (titre, fichier, publié ou test, erreurs). Ta réponse finale tient en 3 lignes.

## Interdits, même en mode auto

- Reddit, commentaires, réponses, messages privés, likes, abonnements, réglages ou profils de comptes : jamais.
- Jamais plus de `max_par_jour` par plateforme, jamais sans crédit, jamais un clip qui a échoué à `verif-regles`.
- Jamais le même clip sur plusieurs comptes d'une même plateforme.
- Ne modifie jamais `mode`, ne crée ni ne lis aucune clé, ne te connecte à aucun compte, n'accepte aucune condition.
- Une chaîne qui a demandé un retrait (`retraits.md`) n'est plus jamais clippée.
