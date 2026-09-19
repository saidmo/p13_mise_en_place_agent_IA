from fastapi import APIRouter, HTTPException

from app.services.youtube_service import YouTubeError, search_videos

router = APIRouter(tags=["youtube"])


@router.get("/videos/{opening}")
def videos(opening: str, max_results: int = 5):
    """Vidéos YouTube explicatives pour une ouverture."""
    try:
        return {"opening": opening, "videos": search_videos(opening, max_results)}
    except YouTubeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc