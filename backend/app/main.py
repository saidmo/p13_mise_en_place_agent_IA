from fastapi import FastAPI

from app.api.v1 import health, moves, evaluate, llm, agent, embeddings, milvus, youtube, mongo
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://[\w.\-]+:4200",   # ← tout hôte, port 4200 (LAN)
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(moves.router, prefix=settings.api_v1_prefix)
app.include_router(evaluate.router, prefix=settings.api_v1_prefix)
app.include_router(llm.router, prefix=settings.api_v1_prefix)
app.include_router(agent.router, prefix=settings.api_v1_prefix)
app.include_router(embeddings.router, prefix=settings.api_v1_prefix) 
app.include_router(milvus.router, prefix=settings.api_v1_prefix)
app.include_router(youtube.router, prefix=settings.api_v1_prefix)
app.include_router(mongo.router, prefix=settings.api_v1_prefix)



@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Agent IA échecs - backend opérationnel"}