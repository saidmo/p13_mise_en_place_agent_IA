from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.services import mongo_service


class YouTubeError(Exception):
    """Erreur lors de l'appel à l'API YouTube."""


def search_videos(query: str, max_results: int = 5) -> list[dict]:
    """Recherche des vidéos YouTube pertinentes (en français) pour une ouverture."""
    key = query.strip().lower()
    cached = mongo_service.cache_get("videos", key)      # ← 1) cache d'abord
    if cached is not None:
        return cached

    if not settings.youtube_api_key:
        raise YouTubeError("YOUTUBE_API_KEY manquante dans la configuration (.env).")
    try:
        youtube = build(
            "youtube", "v3",
            developerKey=settings.youtube_api_key,
            cache_discovery=False,
        )
        response = youtube.search().list(
            q=f"{query} ouverture échecs",
            part="snippet",
            type="video",
            maxResults=max_results,
            relevanceLanguage="fr",
            safeSearch="strict",
        ).execute()
    except HttpError as exc:
        raise YouTubeError(f"Appel YouTube échoué : {exc}") from exc

    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "video_id": video_id,
        })

    mongo_service.cache_set("videos", key, videos)        # ← 2) on persiste en cache

    return videos