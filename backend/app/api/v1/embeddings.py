from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.services.embedding_service import embed_query

router = APIRouter(tags=["embeddings"])


@router.get("/embed-test")
def embed_test(text: str = "Idées et plans dans l'ouverture italienne"):
    """Valide que le modèle d'embeddings tourne et renvoie la bonne dimension."""
    try:
        vec = embed_query(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Embedding échoué : {exc}") from exc
    return {"model": settings.embedding_model, "dim": len(vec), "preview": vec[:5]}