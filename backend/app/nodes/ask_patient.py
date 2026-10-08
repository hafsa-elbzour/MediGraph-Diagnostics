"""Nœud qui utilise le tool ask_patient (pause du graphe jusqu'à la réponse)."""
from app.state import MedicalState
from app.tools.patient_tools import ask_patient


async def ask_patient_node(state: MedicalState) -> dict:
    question = state["current_question"]
    answer = ask_patient(question)  # <- le graphe s'arrête ici, reprend avec la réponse
    return {
        "questions_asked": [*state.get("questions_asked", []), question],
        "patient_answers": [*state.get("patient_answers", []), answer],
        "question_count": state.get("question_count", 0) + 1,
        "messages": [("ai", question), ("human", answer)],
    }
