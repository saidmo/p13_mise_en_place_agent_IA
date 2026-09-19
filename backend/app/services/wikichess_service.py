import httpx
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.embedding_service import embed_documents
from app.services.milvus_service import flush_collection, insert_chunks, reset_collection

WIKIPEDIA_API = "https://fr.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "P13-AgentEchecs/1.0 (projet etudiant OpenClassrooms)"}

# Articles d'ouvertures (Wikipédia FR). Un titre introuvable est ignoré proprement.
DEFAULT_ARTICLES = [
    "Partie italienne",
    "Défense sicilienne",
    "Partie espagnole",
    "Défense française",
    "Gambit dame",
    "Défense Caro-Kann",
    "Partie anglaise",
]

# ~800 caractères par morceau, 100 de chevauchement pour ne pas couper une idée net.
_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)


def fetch_article(title: str) -> str:
    """Texte brut d'un article Wikipédia FR via l'API MediaWiki."""
    params = {
        "action": "query", "format": "json", "prop": "extracts",
        "explaintext": 1, "redirects": 1, "titles": title,
    }
    resp = httpx.get(WIKIPEDIA_API, params=params, headers=HEADERS, timeout=30.0)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    for page in pages.values():
        if page.get("extract", "").strip():
            return page["extract"]
    return ""


def ingest(articles: list[str] | None = None) -> dict:
    """Pipeline complet : repart d'une base propre, puis fetch → chunk → embed → insert."""
    titles = articles or DEFAULT_ARTICLES
    reset_collection()

    per_article, total = {}, 0
    for title in titles:
        text = fetch_article(title)
        if not text:
            per_article[title] = 0
            continue
        chunks = _splitter.split_text(text)
        vectors = embed_documents(chunks)
        rows = [
            {"vector": v, "text": c, "source": f"Wikipédia FR — {title}"}
            for c, v in zip(chunks, vectors)
        ]
        total += insert_chunks(rows)
        per_article[title] = len(chunks)

    flush_collection()
    return {"total_chunks": total, "per_article": per_article}