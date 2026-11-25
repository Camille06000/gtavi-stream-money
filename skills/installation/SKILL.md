---
name: installation
description: Première installation du poste de clips GTA 6. À utiliser quand l'utilisateur installe le plugin, dit « installe », « on commence », « configure la page », ou quand ffmpeg, Python, le venv ou le dossier de la page manquent.
---

# Installation

Fais le travail toi-même. Ne pose à l'utilisateur que les questions listées ici. N'installe rien dans le Python global de l'utilisateur.

## 1. Vérifier les outils (sans question)

- Python 3.10 ou plus : `python --version` (sous Windows, `py -3 --version` si `python` est introuvable). S'il manque ou s'il est trop ancien, dis-le en une ligne et demande à l'utilisateur de l'installer (python.org).
- ffmpeg : `ffmpeg -version`. S'il manque, note la commande d'installation pour le plan (étape 3) : Windows `winget install --id Gyan.FFmpeg -e --source winget`, macOS `brew install ffmpeg`, Linux `sudo apt install -y ffmpeg`.

Ne dépense jamais d'argent et n'ajoute jamais de carte.

## 2. Poser au plus 4 questions, dans UN seul message numéroté

1. Nom de la page et pseudo (@).
2. Plateformes (par exemple X, Instagram Reels, TikTok, YouTube Shorts).
3. Angle de la niche (un seul couloir : astuces et lieux cachés, actu rapide, moments drôles, voitures et customisation).
4. Fuseau horaire (suggestion par défaut : Europe/Paris).

Si l'utilisateur a déjà donné une réponse, ne la redemande pas. Saute ce message si les quatre sont connues.

## 3. Montrer le plan, demander UN seul « oui »

Liste le dossier à créer, les fichiers qu'il contiendra et les installations prévues. Si ffmpeg manque, écris la commande exacte dans le plan : le « oui » doit couvrir cette installation, sinon ne l'installe pas. Après le oui, crée (dans le dossier courant, un dossier au nom de la page) :

- `guide.md` (copie de `${CLAUDE_PLUGIN_ROOT}/skills/routine/references/guide.md`, champs [ENTRE CROCHETS] remplis avec les réponses)
- `faits.md` (faits vérifiés uniquement, chacun avec le lien de sa source officielle)
- `idees.md`, `a-surveiller.md`, `journal.md`
- `scores.csv` avec seulement cette ligne d'en-tête :
  `post_id,date,time,platform,pillar,format,hook,length_sec,credit,views_12h,views_24h,views_72h,likes,reposts_or_shares,replies_or_comments,saves_or_bookmarks,followers_at_read,test_name,notes`
- `apprentissages.md` avec les titres Victoires, Échecs, Règles actuelles
- `retraits.md`
- `campagnes.md` (une ligne de titre et un tableau vide : nom, plateforme, tarif pour 1 000 vues, budget restant, règles, lien, vérifié le ; le format complet est dans `campagnes`)
- `gains.csv` avec l'en-tête `date,campaign,platform,post_url,views,rate_per_1k,est_payout,status` (géré par `scripts/payouts.py`)
- les dossiers `media/officiel`, `media/brut`, `media/montages`

Puis, dans le dossier de la page :

1. `python -m venv .venv` (si `.venv` existe déjà, garde-le).
2. `$PY -m pip install -r "${CLAUDE_PLUGIN_ROOT}/requirements.txt"` (faster-whisper, numpy, requests, yt-dlp, deep-translator, edge-tts, opencv). `$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.
3. ffmpeg, seulement s'il manque et si le oui le couvre. Si winget/brew/apt demande un nouveau terminal pour le PATH, dis-le en une ligne et revérifie.
4. Vérifie : `$PY -c "import faster_whisper, numpy, yt_dlp"` et `ffmpeg -version`.

Pas de réinstallation régulière. Si YouTube renvoie plus tard des erreurs 403, *propose* `$PY -m pip install -U yt-dlp` et attends le oui.

## 4. Clés Twitch (facultatif)

La liste des streams Twitch passe par l'API officielle Helix. Clés gratuites : créer une application sur https://dev.twitch.tv/console, puis mettre `TWITCH_CLIENT_ID` et `TWITCH_CLIENT_SECRET` dans un fichier `.env` du dossier de la page (ou en variables d'environnement). L'utilisateur écrit lui-même ses clés dans `.env` : ne lui demande jamais de les coller dans le chat. Sans clés, Twitch est simplement ignoré dans `streams-live` (YouTube marche sans clé).

## 5. Pilote automatique (facultatif)

Si l'utilisateur veut publier en automatique : copie `${CLAUDE_PLUGIN_ROOT}/skills/pilote-auto/references/pilote.json` dans le dossier de la page (il démarre en `"mode": "test"`) et montre-lui le guide `docs/API-OFFICIELLES.md` du plugin pour brancher YouTube, Instagram et TikTok par les API officielles. Il crée lui-même ses applis développeur, se connecte lui-même et passe lui-même le mode à `auto`. Ne le fais jamais à sa place.

## 6. Terminer

Dis à l'utilisateur, en 3 lignes : ce qui a été installé, où est le dossier, et l'étape suivante (`campagnes`, puis `tendances`).

**Règle absolue : Claude prépare, l'utilisateur publie.** Rappelle-la : l'utilisateur valide chaque publication par un « oui » explicite, rien n'est publié, programmé ni envoyé automatiquement (sauf le pilote automatique, s'il l'active lui-même), et Claude ne s'inscrit ni ne rejoint aucune campagne à sa place.
