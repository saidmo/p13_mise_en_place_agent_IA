from fastapi import APIRouter, HTTPException

from app.services.mongo_service import stats

router = APIRouter(tags=["mongo"])


@router.get("/mongo/stats")
def mongo_stats():
    """État des collections MongoDB (nombre de documents persistés)."""
    try:
        return {"database": "chess_db", "collections": stats()}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"MongoDB indisponible : {exc}") from exc