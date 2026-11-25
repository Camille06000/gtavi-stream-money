---
name: multilangue
description: Transformer un clip fini en versions localisées (français par défaut, puis espagnol, portugais, allemand, italien…) avec sous-titres mot à mot traduits, accroche traduite, voix off de stock facultative sur l'accroche et légendes par plateforme. À utiliser quand l'utilisateur dit « traduis le clip », « fais-le en français », « version FR », « autres langues », « localise ».
---

# Multilangue

Les pages GTA non anglophones sont moins servies : un clip tiré d'un stream anglophone peut nourrir une page française, et d'autres publics ensuite.

À lancer après `decoupe-clip` (le clip doit déjà exister : `jobs/<id>/edits/clip_<n>.mp4` + `.json`) :

`$PY "${CLAUDE_PLUGIN_ROOT}/scripts/translate.py" jobs/<id> --pick <n> [--langs fr] [--voice]`

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

Langue cible par défaut : `fr`. Autres langues : `--langs es,pt,de,it` (par exemple). Sortie dans `jobs/<id>/edits/` : `clip_<n>_<langue>.mp4` par langue et un `clip_<n>_captions.md` avec les légendes X, Instagram et TikTok/Shorts pour chaque langue.

- Mise en page, encadré d'accroche et volume reprennent la découpe d'origine. Corrige avec `--layout`, `--hook`, `--cam` si besoin. Le script ne gère pas la mise en page `react` de `reaction-twitch` (il bascule en `blur`) : pour un clip réaction en français, utilise plutôt `cut.py --translate fr` (voir `reaction-twitch`).
- `--voice` ajoute une voix de synthèse de stock (edge-tts : fr-FR-HenriNeural, es-ES-AlvaroNeural, pt-BR-AntonioNeural, de-DE-ConradNeural, it-IT-DiegoNeural…) qui lit uniquement l'accroche traduite, dans les 2,5 premières secondes, le son d'origine baissé dessous.
- Ne clone et n'imite jamais la voix d'une vraie personne ou d'un streamer. Voix de stock uniquement, et ne présente pas la voix off comme si c'était le créateur qui parlait.

Règles :

1. Traduis les faits, n'invente rien. N'ajoute aucune affirmation, date, prix ou nom absent du clip ou de l'accroche d'origine. La traduction automatique peut déraper (et si un avertissement `translate failed` s'affiche, la ligne est restée dans la langue d'origine) : lis les légendes et l'accroche de chaque langue avant que l'utilisateur publie, et corrige les lignes fausses ou bizarres (demande à l'utilisateur si une langue t'est peu familière).
2. Le fichier de légendes ne contient pas le crédit : ajoute la ligne `🎥 @créateur` à chaque légende.
3. Lance `verif-regles` sur chaque version, comme sur l'original.
4. Publie les versions localisées sur des pages ou comptes séparés par langue, ou en upload multilingue quand la plateforme le permet (par exemple pistes audio multiples et titres traduits sur YouTube). Ne spamme pas une même page avec cinq versions du même clip.
5. Légendes : X sans hashtags ; Instagram 3 à 5 hashtags ; TikTok et Shorts courts avec quelques hashtags.

**Règle absolue : Claude prépare, l'utilisateur publie.** N'uploade rien. Montre les fichiers et les légendes à l'utilisateur et attends un « oui » explicite pour chaque version.
