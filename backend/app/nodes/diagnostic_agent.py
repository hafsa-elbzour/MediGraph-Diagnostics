"""Diagnostic Agent : prépare 5 questions, puis produit la synthèse préliminaire."""
import logging

from app.llm import ask_llm
from app.state import MAX_QUESTIONS, MedicalState
from app.tools import mcp_client
from app.tools.care_tools import recommend_interim_care

logger = logging.getLogger(__name__)

QUESTION_SYSTEM = (
    "Tu es un assistant d'orientation clinique dans un exercice académique. "
    "Pose UNE seule question courte et claire en français pour mieux comprendre "
    "le cas (durée, intensité, antécédents, signes associés...). "
    "Ne répète pas une question déjà posée. Réponds uniquement par la question."
)
SUMMARY_SYSTEM = (
    "Tu rédiges une synthèse clinique préliminaire dans un exercice académique. "
    "Structure : motif, symptômes, éléments importants, points de vigilance. "
    "Ne donne JAMAIS de diagnostic définitif : parle d'orientation préliminaire. "
    "Réponds en français, en 8 lignes maximum."
)


def _history(state: MedicalState) -> str:
    pairs = zip(state.get("questions_asked", []), state.get("patient_answers", []))
    return "\n".join(f"Q: {q}\nR: {a}" for q, a in pairs) or "(aucune)"


async def diagnostic_agent_node(state: MedicalState) -> dict:
    count = state.get("question_count", 0)
    case = state["patient_case"]

    # Phase 1 : encore des questions à poser -> on prépare la prochaine
    if count < MAX_QUESTIONS:
        question = await ask_llm(
            QUESTION_SYSTEM,
            f"Cas : {case}\nÉchanges précédents :\n{_history(state)}\n"
            f"Question numéro {count + 1} sur {MAX_QUESTIONS} :",
        )
        return {"current_question": question}

    # Phase 2 : 5 réponses reçues -> alertes (MCP), synthèse, recommandation
    full_text = case + " " + " ".join(state.get("patient_answers", []))
    try:
        red_flags = await mcp_client.check_red_flags(full_text)
    except mcp_client.MCPError as exc:
        logger.warning("MCP indisponible, aucun signal d'alerte vérifié : %s", exc)
        red_flags = []

    summary = await ask_llm(
        SUMMARY_SYSTEM,
        f"Cas : {case}\nÉchanges :\n{_history(state)}\n"
        f"Signaux d'alerte : {', '.join(red_flags) or 'aucun'}",
    )
    care = await recommend_interim_care(summary, red_flags)
    return {
        "current_question": "",
        "red_flags": red_flags,
        "diagnostic_summary": summary,
        "interim_care": care,
    }
