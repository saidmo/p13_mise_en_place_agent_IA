from langchain_ollama import ChatOllama

from app.core.config import settings


class LLMError(Exception):
    """Erreur lors de l'appel au modèledistant on-premise (Ollama)."""


def get_llm(temperature: float = 0.2) -> ChatOllama:
    """Point d'entrée unique du LLM. L'agent réutilisera ceci, puis .bind_tools()."""
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
        client_kwargs={"timeout": 180},
    )


def ping_llm(prompt: str = "Réponds en une phrase courte : bonjour.") -> dict:
    try:
        result = get_llm().invoke(prompt)
    except Exception as exc:
        raise LLMError(f"Appel Ollama échoué : {exc}") from exc
    return {"model": settings.ollama_model, "reply": result.content}