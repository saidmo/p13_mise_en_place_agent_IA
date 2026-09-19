from langchain_core.tools import tool

from app.services.lichess_service import get_theoretical_moves
from app.services.stockfish_service import evaluate_position
from app.services.milvus_service import search as milvus_search
from app.services.youtube_service import search_videos


@tool
def lichess_opening_moves(fen: str) -> dict:
    """Coups théoriques joués par les maîtres depuis une position FEN (base Masters de Lichess).
    À privilégier tant que la position est une ouverture connue, dans la théorie."""
    return get_theoretical_moves(fen)


@tool
def stockfish_evaluation(fen: str) -> dict:
    """Évaluation moteur d'une position FEN par Stockfish : score en centipions
    (point de vue des Blancs) et meilleur coup. À utiliser quand la position sort
    de la théorie, ou pour une évaluation précise."""
    return evaluate_position(fen)


@tool
def wikichess_context(query: str) -> list[dict]:
    """Recherche du contexte explicatif sur une ouverture (idées stratégiques, plans,
    structure de pions, histoire) dans la base de connaissances Wikichess.
    À utiliser pour les questions de compréhension et d'explication — le POURQUOI —
    plutôt que pour les coups (Lichess) ou l'évaluation chiffrée (Stockfish)."""
    return milvus_search(query, top_k=3)


@tool
def youtube_videos(opening: str) -> list[dict]:
    """Recherche des vidéos YouTube explicatives (en français) sur une ouverture.
    À utiliser quand l'utilisateur veut VOIR une explication en vidéo, une leçon,
    un tutoriel — pas pour les coups, l'évaluation ou le contexte écrit."""
    return search_videos(opening, max_results=3)

  
TOOLS = [lichess_opening_moves, stockfish_evaluation, wikichess_context, youtube_videos]