from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.agent import decide_tools, run_agent
from app.services.llm_service import LLMError

router = APIRouter(tags=["agent"])


class AgentQuery(BaseModel):
    question: str
    fen: str


@router.post("/agent/chat")
def agent_chat(payload: AgentQuery):
    """L'agent complet : exécute les outils et renvoie une réponse finale."""
    try:
        return run_agent(payload.question, payload.fen)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur agent : {exc}") from exc


@router.post("/agent/decide")
def agent_decide(payload: AgentQuery):
    """Diagnostic 3c-i : quels outils le modèle choisit (sans exécuter)."""
    try:
        ai = decide_tools(payload.question, payload.fen)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur agent : {exc}") from exc
    return {"content": ai.content,
            "tool_calls": [{"tool": tc["name"], "args": tc["args"]} for tc in ai.tool_calls]}