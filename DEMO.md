# Fiche de démonstration — Agent IA Ouvertures d'échecs

Six scénarios, à dérouler dans l'ordre (du plus simple au plus impressionnant).
Pour chacun : jouer les coups sur l'échiquier, vérifier la ligne
« Position analysée » (FEN de contrôle), puis poser la question.

> **Avant de commencer** : lancer une question quelconque pour « réveiller » le
> tunnel et charger le modèle sur la PGX. La première vraie réponse devant le
> jury sera ainsi immédiate.

---

## 1. Lichess — coups théoriques

**Coups** : `e2→e4`, `e7→e5`, `g1→f3`, `b8→c6`, `f1→b5` (partie espagnole / Ruy López)
**FEN attendu** : `r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3`
**Question** : « Quels sont les coups les plus joués par les maîtres dans cette position ? »
**À montrer** : reconnaissance de l'ouverture + vraies statistiques (nombre de parties **et** taux de victoire, bien distingués).

## 2. Stockfish — évaluation (position hors théorie légère)

**Coups** : `e2→e4`, `e7→e5`, `g1→f3`, `f7→f6` (défense Damiano, coup fautif)
**FEN attendu** : `rnbqkbnr/pppp2pp/5p2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3`
**Question** : « Quelle est l'évaluation de cette position et le meilleur coup ? »
**À montrer** : net avantage blanc + coup fort (`Nxe5`). Illustre la logique « hors théorie → Stockfish ».

## 3. RAG Wikichess — contexte explicatif

**Coups** : `e2→e4`, `e7→e6`, `d2→d4`, `d7→d5` (défense française)
**FEN attendu** : `rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq d6 0 3`
**Question** : « Explique-moi les idées stratégiques et la structure de pions de la défense française. »
**À montrer** : réponse ancrée dans les passages (fou c8 enfermé, poussée ...c5) — le « pourquoi ».

## 4. YouTube — vidéos

**Coups** : `e2→e4`, `c7→c5` (sicilienne)
**FEN attendu** : `rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2`
**Question** : « Peux-tu me montrer une vidéo pour apprendre la défense sicilienne ? »
**À montrer** : vraies vidéos francophones cliquables issues de l'API (pas d'invention de liens).

## 5. Position piège — hors de toute théorie (fallback gracieux)

**Coups** : `a2→a4`, `a7→a5`, `h2→h4`, `h7→h5` (coups absurdes, aucune partie de maître)
**FEN attendu** : `rnbqkbnr/1pppppp1/8/p6p/P6P/8/1PPPPPP1/RNBQKBNR w KQkq h6 0 3`
**Question** : « Cette position sort de la théorie — que peux-tu me dire, et quel est le meilleur coup ? »
**À montrer** : Lichess ne renvoie **aucun** coup (base vide sur cette position) → l'agent le dit
explicitement et bascule sur **Stockfish** pour l'évaluation et le meilleur coup. C'est la
démonstration de la robustesse « si la partie s'écarte des sentiers battus ».
**Repli si besoin** : si l'agent ne bascule pas seul sur Stockfish, relancer avec
« Alors donne-moi l'évaluation du moteur. »

## 6. Le combiné — orchestration multi-outils (point d'orgue)

**Coups** : `e2→e4`, `c7→c5` (sicilienne)
**FEN attendu** : `rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2`
**Question** : « Donne-moi les meilleurs coups dans cette position, explique l'idée de l'ouverture, et propose une vidéo. »
**À montrer** : sur **une seule demande**, l'agent enchaîne **trois outils**
(Lichess + RAG + YouTube) et produit une réponse unique et synthétique. La
démonstration la plus parlante de l'orchestration LangGraph.

---

