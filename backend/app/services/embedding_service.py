from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings

# Qwen recommande une instruction côté requête (et aucune côté document),
# rédigée en anglais même pour du contenu multilingue.
_QUERY_INSTRUCTION = (
    "Instruct: Given a web search query, retrieve relevant passages "
    "that answer the query\nQuery:"
)


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Charge le modèle une seule fois (au 1er appel), puis le réutilise."""
    return SentenceTransformer(settings.embedding_model)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Vectorise des passages (documents) — sans instruction."""
    vectors = _get_model().encode(texts, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Vectorise une requête — avec l'instruction Qwen (meilleure pertinence)."""
    vector = _get_model().encode(_QUERY_INSTRUCTION + text, normalize_embeddings=True)
    return vector.tolist()