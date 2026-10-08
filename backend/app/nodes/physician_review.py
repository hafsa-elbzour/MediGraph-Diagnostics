"""Physician Review : Human-in-the-Loop, le médecin propose une conduite à tenir."""
from langgraph.types import interrupt

from app.state import MedicalState


async def physician_review_node(state: MedicalState) -> dict:
    treatment = interrupt(
        {
            "type": "physician_review",
            "diagnostic_summary": state.get("diagnostic_summary", ""),
            "interim_care": state.get("interim_care", ""),
            "red_flags": state.get("red_flags", []),
        }
    )
    return {"physician_treatment": treatment}
