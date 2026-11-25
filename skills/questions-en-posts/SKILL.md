---
name: questions-en-posts
description: Transformer les questions que les fans répètent (fils Reddit et commentaires sous nos propres posts) en brouillons de posts tutoriels. À utiliser quand l'utilisateur demande « qu'est-ce que les gens demandent », veut des idées de tutos, ou dit « transforme les questions des commentaires en posts ».
---

# Questions en posts

Trouve les questions que les fans posent en boucle, vérifie si `faits.md` y répond, et rédige des brouillons de posts COMMENT à partir de faits vérifiés uniquement.

## Commande

Depuis le dossier de la page (là où se trouve `faits.md`) :

```
$PY "${CLAUDE_PLUGIN_ROOT}/scripts/questions.py" --subs GTA6,GTA,GrandTheftAutoV --days 3 [--comments commentaires.txt] --out questions.md
```

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

- `--comments commentaires.txt` : commentaires copiés depuis nos propres posts, un par ligne.
- `--facts faits.md` (par défaut), `--ideas idees.md` (par défaut), `--top 25`, `--min-count 1`.
- Utilise le JSON public de Reddit, 1 requête par seconde, attend et réessaie sur une erreur 429. Si Reddit bloque, colle les commentaires dans `commentaires.txt` et relance.

## Ce que tu obtiens

- `questions.md` : groupes de questions classés par nombre puis par votes. Chacun a la question type, le nombre, des liens d'exemple, et soit la ligne de `faits.md` qui y répond, soit la mention « sans réponse : il faut une source officielle ».
- Sous les groupes : un brouillon de tutoriel par groupe qui a une réponse (titre `COMMENT … DANS GTA 6`, étapes numérotées). Le script comprend les questions en français et en anglais.
- `idees.md` : chaque groupe sans réponse y est ajouté comme tâche de recherche.

## Après le lancement

1. Lis chaque brouillon. Le script copie des lignes de `faits.md` ; il ne sait pas juger l'ordre ni si une ligne est vraiment une étape. Remets dans l'ordre, garde 3 à 5 étapes, reste fidèle au fait. Le titre est généré automatiquement depuis la question : reformule-le si besoin selon le modèle « Astuce COMMENT » de `guide.md` (« COMMENT [FAIRE LE TRUC] DANS GTA 6 »), surtout si la question était en anglais.
2. Pour chaque groupe sans réponse, trouve une source officielle et ajoute-la à `faits.md` avec le lien, puis relance.
3. Lance `verif-regles` sur le texte final. Répondre le jour même à une question répétée vaut mieux que du peaufinage.

## Règles

1. Faits uniquement issus de sources officielles (Rockstar, Take-Two, PlayStation, Xbox), notés dans `faits.md` avec le lien. Revérifie tout ce qui a plus de 48 heures.
2. N'invente jamais d'étapes, de chiffres, de dates ni de noms de menus. Pas de source, pas d'étape. Une question sans réponse reste une tâche de recherche.
3. Pas de fuites, rumeurs, piratage, exploits ni astuces « jouer en avance », même si les fans les demandent. Écarte ces groupes.
4. Crédit : si un post s'appuie sur le clip ou la trouvaille d'un fan, crédite avec `🎥 @créateur`. Ne cite pas et ne nomme pas les utilisateurs Reddit ; les questions servent seulement à savoir quoi traiter.
5. Ne laisse jamais entendre que la page est Rockstar. Écris « GTA 6 ».
6. Majuscules uniquement sur la ligne d'accroche.

**Règle absolue : Claude prépare, l'utilisateur publie.** Montre le texte final à l'utilisateur et attends un « oui » explicite. Ne publie, ne programme et ne réponds jamais aux commentaires toi-même : les réponses sont des brouillons que l'utilisateur envoie.
