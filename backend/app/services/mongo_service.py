from pymongo import MongoClient

from app.core.config import settings

_client: MongoClient | None = None


def _get_db():
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=3000)
    return _client[settings.mongo_db]


def cache_get(collection: str, key: str):
    """Lecture cache. Renvoie None si absent OU si Mongo est indisponible."""
    try:
        doc = _get_db()[collection].find_one({"_id": key})
        return doc["data"] if doc else None
    except Exception:
        return None            # ← ne bloque JAMAIS l'agent si Mongo tombe


def cache_set(collection: str, key: str, data) -> None:
    """Écriture cache, best-effort (silencieuse en cas d'échec)."""
    try:
        _get_db()[collection].update_one(
            {"_id": key}, {"$set": {"data": data}}, upsert=True
        )
    except Exception:
        pass


def stats() -> dict:
    """Nombre de documents par collection (pour la démonstration)."""
    db = _get_db()
    return {name: db[name].count_documents({}) for name in db.list_collection_names()}