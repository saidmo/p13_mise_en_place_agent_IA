import httpx

from app.core.config import settings
from app.services import mongo_service

LICHESS_EXPLORER_URL = "https://explorer.lichess.org/masters"


def _headers() -> dict:
    headers = {"User-Agent": "P13-AgentEchecs/1.0 (projet etudiant OpenClassrooms)"}
    if settings.lichess_api_token:
        headers["Authorization"] = f"Bearer {settings.lichess_api_token}"
    return headers


class LichessError(Exception):
    """Erreur lors de l'appel à l'API Lichess."""


def get_theoretical_moves(fen: str, top: int = 5) -> dict:
    """
    Interroge l'explorer d'ouvertures Lichess (base 'masters') et renvoie
    les coups théoriques joués depuis la position FEN.
    """

    cached = mongo_service.cache_get("openings", fen)     # ← cache d'abord
    if cached is not None:
        return cached
    
    try:
        response = httpx.get(
            LICHESS_EXPLORER_URL,
            params={"fen": fen, "moves": top},
            headers=_headers(),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LichessError(f"Appel Lichess échoué : {exc}") from exc

    data = response.json()
    opening = data.get("opening")

    moves = []
    for move in data.get("moves", []):
        total = move["white"] + move["draws"] + move["black"]
        moves.append({
            "san": move["san"],
            "uci": move["uci"],
            "games": total,
            "white_pct": round(100 * move["white"] / total, 1) if total else 0,
            "draw_pct": round(100 * move["draws"] / total, 1) if total else 0,
            "black_pct": round(100 * move["black"] / total, 1) if total else 0,
            "summary": (
                        f"{move['san']} : {total} parties jouées — "
                        f"Blancs {round(100 * move['white'] / total)}%, "
                        f"nulle {round(100 * move['draws'] / total)}%, "
                        f"Noirs {round(100 * move['black'] / total)}%"
                        ),
        })

    result = {
        "fen": fen,
        "opening": opening["name"] if opening else None,
        "eco": opening["eco"] if opening else None,
        "moves": moves,
    }

    mongo_service.cache_set("openings", fen, result)      # ← on persiste 

    return result