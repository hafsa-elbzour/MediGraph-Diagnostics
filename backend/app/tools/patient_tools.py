"""Tool d'interaction avec le patient."""
from langgraph.types import interrupt


def ask_patient(question: str) -> str:
    """Pose une question au patient : le graphe se met en pause (interrupt)
    jusqu'à ce que l'API reprenne avec la réponse du patient."""
    return interrupt({"type": "patient_question", "question": question})
