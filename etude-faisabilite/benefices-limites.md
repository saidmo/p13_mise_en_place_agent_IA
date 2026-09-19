# Bénéfices attendus et limites — Système vidéo → FEN

## 1. Problème adressé

Le système actuel recherche les vidéos par **mots-clés** : une requête
« défense sicilienne » renvoie une vidéo entière, souvent longue et sans
garantie qu'elle traite la position précise que l'utilisateur a sous les yeux.
Le système étudié vise à **indexer les vidéos par les positions qu'elles
affichent réellement**, pour renvoyer la vidéo *et le timestamp exact* d'une
position donnée (FEN).

Cette note évalue les bénéfices attendus, les limites (techniques, juridiques,
économiques), les alternatives, et une feuille de route. L'estimation chiffrée
des coûts fait l'objet d'un livrable séparé.

## 2. Bénéfices attendus

- **Précision et pertinence pédagogique.** L'utilisateur est renvoyé
  directement au passage utile (position + timestamp), et non à une vidéo de
  45 minutes qu'il devra parcourir. La valeur pour un jeune joueur en
  apprentissage est directe : le bon exemple, au bon moment.
- **Un actif de données propre et différenciant.** L'index
  `(position → vidéo → timestamp)` est une ressource construite, propriété du
  projet, difficile à répliquer et réutilisable dans d'autres contextes
  (entraînement, analyse de parties, recommandations).
- **Modularité et interopérabilité (MCP).** Exposé en serveur MCP, le système
  est consommable par l'agent actuel *comme* par d'autres applications, et
  remplaçable sans toucher au reste. C'est une brique, pas un silo.
- **Intégration non intrusive.** Pour l'agent, c'est un outil de plus, au même
  titre que Lichess ou Stockfish. Aucune refonte nécessaire.
- **Un service temps réel léger.** Grâce au découplage ingestion/service, la
  recherche par position reste rapide même si le traitement vidéo en amont est
  coûteux.

## 3. Limites et risques

### 3.1 Techniques — vision par ordinateur

C'est le principal facteur de risque. Les modèles de reconnaissance
*board-to-FEN* sont majoritairement entraînés sur des **échiquiers 2D
numériques propres** ; or les vidéos réelles sont très hétérogènes :

- plateaux **2D numériques** (screencasts Lichess, Chess.com) — cas le plus
  favorable ;
- plateaux **3D physiques** filmés (perspective, ombres, occlusions,
  reconnaissance des pièces) — nettement plus difficile ;
- **annotations** dessinées sur le plateau (flèches, cases surlignées),
  incrustations webcam, animations de coups en cours, compression et faible
  résolution.

Chaque erreur de reconnaissance (une pièce mal classée) produit un **FEN faux**,
donc une entrée d'index erronée. Se pose aussi la question de savoir **quand**
une position est stable (à indexer) plutôt qu'en cours d'animation.

### 3.2 Correspondance de positions

Un **match exact** de FEN est trop rigide : les positions se rejoignent par
**transposition**, et une position « presque identique » (un coup d'écart) ne
serait pas trouvée. Il faut une **similarité de position** plutôt qu'une égalité
stricte — ce qui n'est pas trivial à définir (distance entre positions). Le
bruit de reconnaissance (§3.1) risque en outre de polluer l'index de fausses
positions.

### 3.3 Juridiques et conformité (RGPD / droit d'auteur)

- Les **CGU de YouTube** interdisent en général le téléchargement et le
  stockage des vidéos sans autorisation. **Mitigation** : traiter les frames
  **à la volée** (en flux) sans jamais stocker la vidéo ni les images — ne
  conserver que `(URL, timestamp, FEN)`. On ne réhéberge rien ; on renvoie vers
  la vidéo d'origine, ce qui reste favorable aux créateurs.
- **Données personnelles** : le contenu échiquéen n'en comporte guère, mais des
  **visages** peuvent apparaître (webcams). Le traitement transitoire des
  frames, sans stockage d'images, est aussi le bon réflexe RGPD.
- **Quota** de l'API YouTube à respecter côté collecte.

### 3.4 Économiques et business

- **Coût de calcul** : l'ingestion (extraction de frames × modèle CV × volume de
  vidéos) est gourmande en GPU — poste principal, détaillé dans l'étude de
  coûts.
- **Amorçage (cold start)** : la valeur dépend d'un catalogue déjà indexé ; tant
  qu'il est mince, la couverture est faible. Beaucoup de positions n'auront
  aucune vidéo associée.
- **Maintenance continue** : nouveaux contenus à ingérer, modèles à surveiller,
  dérive dans le temps.
- **Dépendance à YouTube** : risque de plateforme (évolution des CGU, de l'API).
- **Rapport coût/valeur** : le gain de précision justifie-t-il le surcoût face à
  une recherche textuelle enrichie ? Question à trancher selon l'usage réel.

### 3.5 Qualité et couverture de service

Une position n'est trouvable que si une vidéo indexée la montre. La **longue
traîne** des positions rares restera non couverte, et la qualité perçue dépendra
directement de la richesse et de la propreté de l'index.

## 4. Alternatives envisageables

| Approche | Principe | Coût | Précision | Verdict |
|---|---|---|---|---|
| **A. Recherche textuelle enrichie** (actuelle) | Requête par mots-clés + métadonnées | Faible | Faible (vidéo entière) | Base de départ |
| **B. Transcriptions + chapitres** | Recherche dans les sous-titres/chapitres YouTube pour localiser un sujet | Faible/moyen | Moyenne (par sujet, pas par position) | Bon compromis, sans vision |
| **C. Pipeline vidéo → FEN** (étudié) | Indexation par position via CV | Élevé | Élevée (position + timestamp) | Cible, sur périmètre maîtrisé |
| **D. Hybride** | B pour dégrossir, C sur un catalogue restreint et curé | Moyen | Élevée sur le périmètre couvert | Recommandé à moyen terme |

L'alternative **B** (transcriptions/chapitres) mérite d'être soulignée : elle
n'exige **aucune vision par ordinateur**, s'appuie sur des données déjà fournies
par YouTube, et offre déjà un gain net sur la recherche actuelle — à considérer
comme jalon intermédiaire.

## 5. Conditions de réussite et feuille de route

Le système est faisable et à valeur ajoutée **à condition de cadrer le
périmètre**. Feuille de route proposée :

- **Phase 0 — Preuve de reconnaissance.** Ingestion de quelques vidéos en 2D
  numérique ; **mesurer la précision réelle** du board-to-FEN avant tout
  industrialisation. C'est le go/no-go technique.
- **Phase 1 — MVP.** Serveur MCP + index sur un catalogue restreint de
  screencasts 2D, correspondance exacte. Intégration à l'agent.
- **Phase 2 — Robustesse.** Similarité de positions (transpositions), élargissement
  du catalogue, traitement à la volée pour la conformité.
- **Phase 3 — Extension.** Plateaux 3D/physiques (plus difficiles),
  passage à l'échelle de l'ingestion, éventuel volet transcriptions (approche D).

## 6. Synthèse — verdict de faisabilité

Le système apporte une **valeur pédagogique réelle** (le bon passage vidéo pour
la position exacte) et un **actif de données différenciant**, dans une
architecture modulaire et propre (MCP). Sa faisabilité est **conditionnelle** :
les risques se concentrent sur la **précision de la vision par ordinateur en
conditions réelles hétérogènes** et sur la **conformité** (CGU / droit
d'auteur). Ces deux risques se maîtrisent par le **cadrage** : commencer par le
2D numérique, traiter les frames à la volée, viser la similarité plutôt que
l'exactitude, et valider la précision sur un POC d'ingestion avant d'investir.
Une approche hybride (transcriptions d'abord, vision ensuite) constitue un
chemin progressif à moindre risque.
