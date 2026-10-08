"""État partagé du graphe : la « mémoire » que tous les nœuds lisent et complètent."""
from typing import Annotated, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

MAX_QUESTIONS = 5
DISCLAIMER = "Ce système ne remplace pas une consultation médicale."


class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]  # historique (ajouté, jamais écrasé)
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    patient_case: str          # cas initial saisi par le patient
    current_question: str      # question en attente de réponse
    questions_asked: list[str]
    patient_answers: list[str]
    question_count: int
    red_flags: list[str]       # signaux d'alerte détectés via MCP
    diagnostic_summary: str    # synthèse clinique préliminaire
    interim_care: str          # recommandation intermédiaire
    physician_treatment: str   # conduite à tenir saisie par le médecin
    final_report: str
