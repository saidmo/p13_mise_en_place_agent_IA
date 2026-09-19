from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

from app.agent.tools import TOOLS
from app.services.llm_service import get_llm

SYSTEM_PROMPT = (
    "Tu es un assistant d'échecs qui aide de jeunes joueurs à travailler leurs ouvertures.\n\n"
    "RÈGLES STRICTES :\n"
    "- Utilise TOUJOURS tes outils pour toute information sur une position "
    "(coups théoriques via Lichess, évaluation via Stockfish). Tu ne dois JAMAIS inventer "
    "de coups, de statistiques ou d'évaluations : tes connaissances internes aux échecs ne sont pas fiables.\n"
    "- Fonde ta réponse UNIQUEMENT sur les données renvoyées par les outils. Cite les chiffres "
    "concrets : nombre de parties, pourcentages de victoire/nulle/défaite, nom de l'ouverture "
    "s'il est fourni. N'ajoute aucune affirmation générale qui ne soit pas appuyée par ces données.\n"
    "- Si un outil ne renvoie aucun coup (position sortie de la théorie), dis-le explicitement "
    "et appuie-toi sur l'évaluation de Stockfish.\n\n"
    "- Pour les questions de COMPRÉHENSION (idées d'une ouverture, plans, pourquoi tel coup), "
    "utilise l'outil de contexte Wikichess, et appuie ta réponse sur les passages retournés "
    "en citant l'ouverture concernée.\n"
    "- Pour l'évaluation, rapporte les champs 'summary' et 'eval_pawns' (en pions) de Stockfish ; "
    "n'utilise jamais 'cp' brut et ne fais aucune conversion toi-même.\n"
    "- Quand l'utilisateur demande une vidéo, une leçon filmée ou veut VOIR une explication, "
    "utilise l'outil vidéos YouTube et présente les titres avec leurs liens cliquables.\n"
    "- N'invente JAMAIS de lien vidéo. Ne fournis une URL YouTube que si elle provient "
    "directement de l'outil vidéos ; si tu n'as pas appelé cet outil, ne propose aucune vidéo "
    "et ne fabrique aucun lien.\n"
    "- Dans les données Lichess, 'games' est le NOMBRE de parties et 'white_pct'/'draw_pct'/"
    "'black_pct' sont des taux de résultat : ne confonds jamais la fréquence d'un coup avec son "
    "taux de victoire, et n'exprime pas un nombre de parties en pourcentage.\n"
    "- Pour les coups Lichess, rapporte le champ 'summary' de chaque coup tel quel, "
    "sans reformuler les chiffres.\n"
    "- n'invente jamais de liens de videos youtube de type youtube.com/watch?v=example1, youtube.com/watch?v=example2, etc. \n"
    " tous les liens doivent provenir de l'outil vidéos YouTube et être réels.\n\n"
    "STYLE : français clair, pédagogique et concis, adapté à un jeune joueur. Présente les "
    "meilleurs coups avec leurs statistiques réelles, puis une brève explication."
)

# Le LLM outillé, instancié une seule fois.
llm_with_tools = get_llm(temperature=0).bind_tools(TOOLS)


def agent_node(state: MessagesState) -> dict:
    """Nœud LLM : décide d'appeler un outil, ou rédige la réponse finale."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def should_continue(state: MessagesState) -> str:
    """Arête conditionnelle : reste-t-il des outils à exécuter ?"""
    return "tools" if state["messages"][-1].tool_calls else END


def build_agent():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


# Graphe compilé une fois, réutilisé à chaque requête.
agent_graph = build_agent()


def run_agent(question: str, fen: str) -> dict:
    """Exécute le graphe complet et renvoie la réponse finale + la trace des outils."""
    initial = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Position (FEN) : {fen}\n\nQuestion : {question}"),
    ]
    result = agent_graph.invoke({"messages": initial})

    tools_used = [
        {"tool": tc["name"], "args": tc["args"]}
        for msg in result["messages"]
        for tc in getattr(msg, "tool_calls", []) or []
    ]
    return {"answer": result["messages"][-1].content, "tools_used": tools_used}


def decide_tools(question: str, fen: str):
    """3c-i (diagnostic) : le modèle choisit les outils sans les exécuter."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Position (FEN) : {fen}\n\nQuestion : {question}"),
    ]
    return llm_with_tools.invoke(messages)