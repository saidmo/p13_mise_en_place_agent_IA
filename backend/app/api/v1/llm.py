from fastapi import APIRouter, HTTPException

from app.services.llm_service import LLMError, ping_llm

router = APIRouter(tags=["llm"])


@router.get("/llm-ping")
def llm_ping():
    """Vérifie la liaison backend ↔ Ollama distant installé sur la machine PGX."""
    try:
        return ping_llm()
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc