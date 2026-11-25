# Brancher la publication automatique sur les API officielles

Le pilote automatique (`pilote-auto`) publie par les API officielles de YouTube, Instagram et TikTok. C'est gratuit et sans service intermédiaire, mais chaque plateforme demande une petite « appli développeur » à ton nom. **C'est toi qui crées ces applis et qui te connectes** : Claude ne saisit jamais un mot de passe ni une clé à ta place.

Tout se range dans le dossier de ta page :

```
ma-page-gta/
├─ .env                      ← tes clés (tu les écris toi-même, jamais dans le chat)
├─ jetons/                   ← connexions enregistrées par publish.py (ne jamais publier ce dossier)
│  └─ youtube_client_secret.json
└─ pilote.json               ← réglages du pilote ; "mode": "test" tant que tu n'as pas tout vérifié
```

Une fois une plateforme branchée, vérifie avec :

```
.venv\Scripts\python.exe <chemin du plugin>\scripts\publish.py check
```

## À savoir avant de commencer

| | Publication publique dès le départ ? | Ce qui la débloque |
|---|---|---|
| Instagram | Oui, sur ton propre compte | Rien de plus (ton compte est « testeur » de ta propre appli) |
| YouTube | Non : les vidéos envoyées par une appli non auditée restent privées | Le formulaire d'audit gratuit de YouTube (quelques semaines) |
| TikTok | Non : publication en privé uniquement tant que l'appli n'est pas auditée | L'audit de l'API Content Posting de TikTok |

En attendant les audits, `publish.py` envoie quand même : la vidéo arrive en privé (statut « en ligne privée » dans `publications.csv`) et tu peux la passer en public à la main en deux clics.

---

## 1. Instagram (le plus rapide)

1. Passe ton compte Instagram en **compte professionnel** (Créateur ou Entreprise) : Paramètres → Type de compte et outils.
2. Va sur [developers.facebook.com](https://developers.facebook.com), crée une appli, et choisis le cas d'usage qui gère le **contenu Instagram** (API Instagram avec connexion Instagram).
3. Dans la configuration de l'API Instagram, **ajoute ton compte Instagram** (rôle testeur). Accepte l'invitation dans l'appli Instagram (Paramètres → Applis et sites web → Invitations de testeur).
4. Clique sur **Générer un jeton** pour ton compte. Les autorisations nécessaires sont `instagram_business_basic` et `instagram_business_content_publish`.
5. Colle le jeton dans `.env` :
   ```
   INSTAGRAM_ACCESS_TOKEN=le_jeton_généré
   ```
6. Lance `publish.py auth instagram`. Le jeton est vérifié, renouvelé pour 60 jours et rangé dans `jetons/`. Le pilote le renouvelle tout seul chaque lundi.

## 2. YouTube

1. Va sur [console.cloud.google.com](https://console.cloud.google.com) et crée un projet (ex. « clips-gta »).
2. **API et services → Bibliothèque** : active **YouTube Data API v3**.
3. **Écran de consentement OAuth** : type « Externe », nom de l'appli, ton e-mail. Ajoute les champs d'application `youtube.upload` et `youtube.readonly`, et ton compte Google comme utilisateur test.
4. Passe l'appli **en production** (bouton « Publier l'application »). Sinon Google coupe la connexion au bout de 7 jours. À la connexion, Google affichera « appli non validée » : normal pour un usage perso, clique sur « Paramètres avancés » puis continue.
5. **Identifiants → Créer → ID client OAuth → Application de bureau**. Télécharge le JSON, renomme-le `youtube_client_secret.json` et range-le dans `jetons/`.
6. Lance `publish.py auth youtube` : ton navigateur s'ouvre, tu choisis la chaîne et tu acceptes. C'est fait une fois pour toutes.
7. Pour publier en public : remplis le formulaire **« YouTube API Services – Audit and Quota Extension »** depuis la console Google. Par défaut, le quota permet environ 6 envois par jour, ce qui suffit pour le pilote (4 par jour).

## 3. TikTok

1. Crée un compte sur [developers.tiktok.com](https://developers.tiktok.com), puis **Manage apps → Connect an app**.
2. Ajoute les produits **Login Kit** et **Content Posting API** (active « Direct Post »). Les autorisations sont `user.info.basic` et `video.publish`.
3. Déclare l'adresse de retour `http://localhost:8765/callback/`. Si TikTok refuse une adresse locale, dis-le à Claude : on passera par une petite page de redirection.
4. Copie la **Client key** et le **Client secret** dans `.env` :
   ```
   TIKTOK_CLIENT_KEY=...
   TIKTOK_CLIENT_SECRET=...
   TIKTOK_REDIRECT_URI=http://localhost:8765/callback/
   ```
5. Lance `publish.py auth tiktok` et connecte-toi dans le navigateur.
6. Pour publier en public : soumets l'appli à l'audit TikTok (Content Posting API). Avant l'audit, les vidéos partent en privé.

---

## Activer le pilote

1. `publish.py check` affiche « prêt » pour les plateformes branchées.
2. Fais tourner un passage en `"mode": "test"` et regarde `journal.md` et les clips produits.
3. Quand tout te va, passe `"mode": "auto"` dans `pilote.json`. **C'est toi qui fais ce changement** ; le pilote ne le fait jamais.
4. Pour tout arrêter d'un coup, crée un fichier vide `PAUSE` dans le dossier de la page.

## Garde-fous qui restent actifs en mode auto

- Plafond par plateforme et par jour (`max_par_jour`), crédit `🎥 @créateur` obligatoire, `verif-regles` obligatoire.
- Jamais de Reddit, de commentaire, de réponse, de message privé, de like ni de changement de réglages de compte.
- Une chaîne qui a demandé un retrait n'est plus jamais clippée.
