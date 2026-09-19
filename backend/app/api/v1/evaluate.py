from fastapi import APIRouter, HTTPException, Query

from app.services.stockfish_service import StockfishError, evaluate_position

router = APIRouter(tags=["evaluate"])


@router.get("/evaluate/{fen:path}")
def evaluate(fen: str, depth: int = Query(15, ge=1, le=30)):
    """Évaluation Stockfish d'une position FEN (centipions, point de vue Blancs)."""
    try:
        return evaluate_position(fen, depth=depth)
    except StockfishError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc