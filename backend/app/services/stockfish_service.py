import chess
import chess.engine

from app.core.config import settings


class StockfishError(Exception):
    """Erreur lors de l'analyse Stockfish."""


def evaluate_position(fen: str, depth: int = 15) -> dict:
    """
    Évalue une position FEN avec Stockfish.
    Renvoie l'évaluation (centipions, point de vue des Blancs) et le meilleur coup.
    """
    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise StockfishError(f"FEN invalide : {exc}") from exc

    try:
        with chess.engine.SimpleEngine.popen_uci(settings.stockfish_path) as engine:
            info = engine.analyse(board, chess.engine.Limit(depth=depth))
    except (FileNotFoundError, chess.engine.EngineError) as exc:
        raise StockfishError(f"Analyse Stockfish échouée : {exc}") from exc

    score = info["score"].white()
    pv = info.get("pv") or []
    best_move = pv[0] if pv else None

    return {
        "fen": fen,
        "depth": depth,
        "turn": "white" if board.turn else "black",
        "cp": score.score(),          # centipions (100 = +1 pion), None si mat forcé
        "mate_in": score.mate(),      # nb de coups avant mat, None sinon
        "best_move": board.san(best_move) if best_move else None,
        "best_move_uci": best_move.uci() if best_move else None,
    }