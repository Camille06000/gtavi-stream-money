---
name: campagnes
description: Trouver les campagnes de clipping GTA 6 et gaming en cours sur Whop Content Rewards et Clip, et les noter dans campagnes.md. À utiliser quand l'utilisateur dit « trouve les campagnes », « où gagner de l'argent », « quelles campagnes sont ouvertes », « combien pour 1 000 vues », ou « mets à jour campagnes.md ».
---

# Campagnes

Lis les pages en direct. Ne te fie pas à ta mémoire : tarifs et budgets changent tous les jours.

1. Consulte ces sources, avec les outils de navigateur ou en récupérant les pages :
   - Whop Content Rewards : `https://whop.com/discover/` (cherche « GTA 6 », « GTA VI », « gaming clipping », « content rewards ») et les pages publiques des campagnes sur `https://contentrewards.com/` (les liens ressemblent à `contentrewards.com/c/campaigns/<id>`).
   - Clip (Clip Tech, LLC) : `https://www.clip.tech/clippers` liste les campagnes en cours avec le tarif pour 1 000 vues et la part de budget restante, sans connexion. Les briefs et règles sont sur leur Discord : demande à l'utilisateur de les coller. Leurs conditions disent que les paiements se font à Net 30 après la fin d'une campagne et dépendent du paiement du client ; dis-le à l'utilisateur en une ligne.
2. Pour chaque campagne qui semble active, ouvre sa page et note :
   - nom et créateur ou marque
   - plateformes acceptées
   - tarif pour 1 000 vues (et tout plafond par clip ou par personne)
   - budget restant ou budget total
   - règles clés : contenu source autorisé, durée minimale, crédit exigé, hashtags, contenus interdits, processus de validation
   - lien
   - date de vérification
3. Écris ou mets à jour `campagnes.md` : une ligne par campagne dans le tableau (nom, plateforme, tarif pour 1 000 vues, budget restant, règles, lien, vérifié le), puis une section par campagne que `verif-regles` sait lire :

   ```
   ## <nom de la campagne>
   duree_min: 15
   duree_max: 60
   hashtags_obligatoires: #a #b
   mention_obligatoire: @x
   Règles collées : <texte>
   ```

   N'écris une ligne `duree_min`, `duree_max`, `hashtags_obligatoires` ou `mention_obligatoire` que si la valeur est visible sur la page ou dans les règles collées. Si une valeur n'est pas visible, écris `inconnu` dans le tableau. N'estime et n'invente jamais un chiffre.
4. Règles derrière une connexion : dis à l'utilisateur de quelle campagne il s'agit et demande-lui de coller le texte des règles. Enregistre-le dans `campagnes.md` sous cette campagne. N'essaie jamais de te connecter, de rejoindre une campagne ni d'accepter des conditions à sa place.
5. Écarte toute campagne qui demande des fuites, du « jouer en avance », du piratage, de l'argent GTA Online ou des bots AFK, ou de faux comptes. Dis pourquoi en une ligne.
6. Donne une courte liste classée : campagne, tarif, budget restant, effort. Aucune promesse de gains : la paie dépend des vues validées et des règles propres à chaque campagne.

**Règle absolue : Claude prépare, l'utilisateur publie.** L'utilisateur rejoint les campagnes et soumet les clips lui-même. Toi, tu prépares et tu vérifies les clips.
