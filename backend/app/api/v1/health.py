from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    """Vérifie que l'API répond. Sert à valider le conteneur Docker."""
    return {"status": "ok"}