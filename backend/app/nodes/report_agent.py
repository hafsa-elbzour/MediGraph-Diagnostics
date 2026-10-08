"""Report Agent : génère le rapport final structuré."""
from app.llm import ask_llm
from app.state import DISCLAIMER, MedicalState

REPORT_SYSTEM = (
    "Tu rédiges un rapport d'orientation clinique SIMULÉ (exercice académique), en "
    "français, avec les sections : 1. Cas initial, 2. Réponses du patient, "
    "3. Synthèse clinique préliminaire, 4. Recommandation intermédiaire, "
    "5. Conduite à tenir proposée par le médecin. Ne donne aucun diagnostic définitif."
)


async def report_agent_node(state: MedicalState) -> dict:
    qa = "\n".join(
        f"Q: {q}\nR: {a}"
        for q, a in zip(state.get("questions_asked", []), state.get("patient_answers", []))
    )
    body = await ask_llm(
        REPORT_SYSTEM,
        f"Cas initial : {state['patient_case']}\nÉchanges :\n{qa}\n"
        f"Synthèse : {state['diagnostic_summary']}\n"
        f"Recommandation intermédiaire : {state['interim_care']}\n"
        f"Conduite à tenir du médecin : {state['physician_treatment']}",
    )
    # La mention obligatoire est ajoutée par le code : on ne dépend pas du LLM.
    return {"final_report": f"{body}\n\n---\n{DISCLAIMER}"}
