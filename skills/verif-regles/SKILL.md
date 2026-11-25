---
name: verif-regles
description: Vérifier un clip fini avant publication : specs techniques, règles de la campagne et contenus interdits. À utiliser avant chaque upload, ou quand l'utilisateur demande « je peux poster ça ? », « vérifie le clip », « c'est conforme ? ».
---

# Vérif règles

Lance :

`$PY "${CLAUDE_PLUGIN_ROOT}/scripts/check.py" jobs/<id>/edits/clip_<n>.mp4 --campaign campagnes.md --caption "texte de la légende"`

`$PY` = le Python du venv de la page : `.venv\Scripts\python.exe` sous Windows, `.venv/bin/python` sous macOS/Linux. Lance toujours depuis le dossier de la page.

Le script vérifie : 1080x1920, environ 30 images/s, présence du son, durée (`duree_min` / `duree_max` de la campagne, sinon 7 à 60 s par défaut), termes interdits en anglais et en français dans l'accroche et la légende (fuites, « jouer en avance », piratage, glitch d'argent…), et, si la campagne les exige, les hashtags (`hashtags_obligatoires`) et la mention (`mention_obligatoire`) dans la légende passée avec `--caption`. Il lit la première valeur de chaque clé trouvée dans le fichier : si `campagnes.md` contient plusieurs campagnes, copie la section de la campagne visée dans `jobs/<id>/campagne.md` et passe ce fichier à `--campaign`.

Ensuite :

1. Montre OK ou ÉCHEC pour chaque contrôle, en liste courte (le script termine par `RÉSULTAT : OK` ou `RÉSULTAT : ÉCHEC`).
2. Sur un ÉCHEC : corrige la cause (redécoupe avec `decoupe-clip`, ajoute le crédit, raccourcis) et relance. Ne discute pas un contrôle échoué.
3. Relis aussi la légende toi-même. Elle doit créditer le créateur dans le texte (`🎥 @créateur`), sans fait inventé, sans le mot « officiel », et respecter les règles de légende de la plateforme dans `guide.md`. La liste de termes interdits du script n'est pas exhaustive : repère aussi les tournures qu'elle ne connaît pas.
4. Le script ne peut pas tout juger. Si les règles de la campagne sont `inconnu` ou absentes, demande à l'utilisateur de les coller.

**Règle absolue : Claude prépare, l'utilisateur publie.** Seulement quand tous les contrôles passent, envoie à l'utilisateur le clip, la légende et le crédit, et attends un « oui » explicite. C'est l'utilisateur qui publie. N'uploade jamais rien automatiquement.
