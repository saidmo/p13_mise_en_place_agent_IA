from fastapi import APIRouter, HTTPException

from app.services.milvus_service import MilvusError, collection_stats, ensure_collection, search

from app.services.wikichess_service import ingest


router = APIRouter(tags=["milvus"])


@router.post("/milvus/init")
def milvus_init():
    """Crée la collection si besoin."""
    try:
        return ensure_collection()
    except MilvusError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/milvus/stats")
def milvus_status():
    """État de la collection (existence + nombre de vecteurs)."""
    try:
        return collection_stats()
    except MilvusError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
        
@router.post("/milvus/ingest")
def milvus_ingest():
    """Récupère les articles Wikichess, les découpe, les vectorise et les insère."""
    try:
        return ingest()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ingestion échouée : {exc}") from exc
        

@router.get("/vector-search")
def vector_search(query: str, top_k: int = 5):
    """Recherche les passages les plus pertinents pour une question."""
    try:
        return {"query": query, "results": search(query, top_k)}
    except MilvusError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc