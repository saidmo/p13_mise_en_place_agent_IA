from pymilvus import MilvusClient, DataType

from app.core.config import settings

from app.services.embedding_service import embed_query

class MilvusError(Exception):
    """Erreur lors d'une opération Milvus."""


def get_client() -> MilvusClient:
    """Client Milvus (léger, réouvrable à chaque appel pour un POC)."""
    return MilvusClient(uri=settings.milvus_uri)


def ensure_collection() -> dict:
    """Crée la collection si elle n'existe pas. Idempotent."""
    try:
        client = get_client()
        if client.has_collection(settings.milvus_collection):
            return {"collection": settings.milvus_collection, "created": False}

        schema = client.create_schema(auto_id=True, enable_dynamic_field=True)
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=settings.embedding_dim)
        schema.add_field("text", DataType.VARCHAR, max_length=8192)
        schema.add_field("source", DataType.VARCHAR, max_length=512)

        index_params = client.prepare_index_params()
        index_params.add_index(field_name="vector", metric_type="COSINE", index_type="AUTOINDEX")

        client.create_collection(
            collection_name=settings.milvus_collection,
            schema=schema,
            index_params=index_params,
        )
        return {"collection": settings.milvus_collection, "created": True}
    except Exception as exc:
        raise MilvusError(f"Opération Milvus échouée : {exc}") from exc


def collection_stats() -> dict:
    """Infos de base : existence + nombre d'entités."""
    try:
        client = get_client()
        exists = client.has_collection(settings.milvus_collection)
        count = 0
        if exists:
            client.load_collection(settings.milvus_collection)
            count = client.query(
                settings.milvus_collection, filter="", output_fields=["count(*)"]
            )[0]["count(*)"]
        return {"collection": settings.milvus_collection, "exists": exists, "count": count}
    except Exception as exc:
        raise MilvusError(f"Lecture Milvus échouée : {exc}") from exc
        
def reset_collection() -> None:
    """Supprime la collection si elle existe, puis la recrée vide (repart propre)."""
    client = get_client()
    if client.has_collection(settings.milvus_collection):
        client.drop_collection(settings.milvus_collection)
    ensure_collection()


def insert_chunks(rows: list[dict]) -> int:
    """Insère des lignes {vector, text, source} dans la collection."""
    if not rows:
        return 0
    get_client().insert(settings.milvus_collection, rows)
    return len(rows)


def flush_collection() -> None:
    """Force l'écriture pour que le compte soit immédiatement exact."""
    get_client().flush(settings.milvus_collection)
    

def search(query: str, top_k: int = 5) -> list[dict]:
    """Vectorise la requête et renvoie les top_k passages les plus proches."""
    try:
        client = get_client()
        client.load_collection(settings.milvus_collection)
        vector = embed_query(query)
        results = client.search(
            collection_name=settings.milvus_collection,
            data=[vector],
            limit=top_k,
            output_fields=["text", "source"],
            search_params={"metric_type": "COSINE"},
        )
    except Exception as exc:
        raise MilvusError(f"Recherche Milvus échouée : {exc}") from exc

    hits = results[0] if results else []
    return [
        {
            "score": round(h["distance"], 4),
            "source": h["entity"]["source"],
            "text": h["entity"]["text"],
        }
        for h in hits
    ]