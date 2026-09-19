from fastapi import APIRouter, HTTPException

from app.services.lichess_service import LichessError, get_theoretical_moves

router = APIRouter(tags=["moves"])


@router.get("/moves/{fen:path}")
def theoretical_moves(fen: str):
    """Coups théoriques (base Masters de Lichess) pour une position FEN."""
    try:
        return get_theoretical_moves(fen)
    except LichessError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc