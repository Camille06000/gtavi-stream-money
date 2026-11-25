---
name: carte-secrets
description: Construire et publier une carte vérifiée des lieux cachés, voitures rares, objets à collectionner, spots d'argent et easter eggs de GTA 6 trouvés par des créateurs. À utiliser quand l'utilisateur veut des secrets, des lieux cachés, des easter eggs ou des posts astuces intemporels « caché à Leonida », ou dit « scanne cette vidéo pour les secrets ».
---

# Carte des secrets

Les entrées vivent dans `secrets.csv` (id, category, name, where, how, source_channel, source_url_with_timestamp, found_on, status, verified_by, notes). Catégories : place, money, car, collectible, easter_egg, other. Statuts : unverified, verified, wrong.

## Commandes

Depuis le dossier de la page : `$PY "${CLAUDE_PLUGIN_ROOT}/scripts/secrets_map.py" ...` (`--csv chemin` avant la sous-commande pour un autre fichier).

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

- `scan jobs/<id>` : lit `transcript.json` et `info.json`, repère les mentions de type secret, en français et en anglais (caché, secret, easter egg, argent, planque, objets de collection, voiture rare, emplacement, débloquer… / hidden, money, stash, collectible, rare car, location, spawn, unlock) et les ajoute en `unverified` avec une citation et un lien `?t=` vers la source. Les doublons sont ignorés. Les mentions de type exploit sont ignorées et affichées.
- `add --name N --where W --how H --category place --channel C --url U` : entrée manuelle.
- `verify <id> --by "<qui/comment>"` : seulement après vérification du spot en jeu (ou confirmation par du matériel officiel). Exige where, how et source_channel remplis.
- `wrong <id>` : l'astuce ne tient pas.
- `posts` : brouillons « COMMENT TROUVER … DANS GTA 6 » et « coup de projecteur » pour chaque entrée vérifiée, plus un plan de carrousel « N lieux cachés à Leonida » dès que 3 entrées ou plus sont vérifiées. Écrit `posts-secrets.md`.
- `map` : tableau groupé par catégorie. Écrit `carte-secrets.md`.

## Déroulé

1. `scan` sur une vidéo transcrite. Ouvre chaque lien `?t=`, lis la citation et réécris dans `secrets.csv` le nom, le lieu et la méthode en une vraie astuce.
2. Vérifie en jeu. `verify` ou `wrong`.
3. `posts`, relis et ajuste les brouillons (ils sortent déjà en français), puis lance `verif-regles` dessus avant qu'ils partent.

## Règles

1. Ne publie que des entrées vérifiées. Une entrée non vérifiée est une piste, pas un fait.
2. Crédite celui qui a trouvé sur chaque post (`🎥 chaîne` plus le lien horodaté). Ne présente jamais la trouvaille d'un créateur comme la nôtre.
3. Pas de glitchs, exploits, glitchs d'argent, duplication, fuites ni contenu « jouer en avance ». Le script les refuse ; ne le contourne pas.
4. La sortie du scan est une supposition tirée de la transcription. Réécris le nom, le lieu et la méthode à la main ; ne publie pas la citation brute.
5. Pas de spoiler sur l'histoire pendant la semaine de sortie. Ne laisse jamais entendre que la page est Rockstar. Écris « GTA 6 ». Pas de hashtags sur X.

**Règle absolue : Claude prépare, l'utilisateur publie.** Montre les visuels et la légende, puis attends un « oui » explicite pour chaque post. Ne publie et ne programme jamais rien toi-même.
