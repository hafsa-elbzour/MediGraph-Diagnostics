"""Supervisor : lit le State et décide du prochain nœud (aucun appel LLM)."""
from app.state import MedicalState


async def supervisor_node(state: MedicalState) -> dict:
    if not state.get("diagnostic_summary"):
        return {"next": "diagnostic_agent"}
    if not state.get("physician_treatment"):
        return {"next": "physician_review"}
    if not state.get("final_report"):
        return {"next": "report_agent"}
    return {"next": "FINISH"}
