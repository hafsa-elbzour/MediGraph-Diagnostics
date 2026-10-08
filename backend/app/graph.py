"""Assemblage du graphe LangGraph.

START -> supervisor -> diagnostic_agent <-> ask_patient (x5)
      -> supervisor -> physician_review -> supervisor -> report_agent -> supervisor -> END
"""
from langgraph.graph import END, START, StateGraph

from app.nodes.ask_patient import ask_patient_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node
from app.nodes.supervisor import supervisor_node
from app.state import MedicalState


def route_from_supervisor(state: MedicalState) -> str:
    return state["next"]


def route_after_diagnostic(state: MedicalState) -> str:
    # Synthèse prête -> retour au Supervisor ; sinon on pose la question préparée
    return "supervisor" if state.get("diagnostic_summary") else "ask_patient"


def build_graph(checkpointer=None):
    builder = StateGraph(MedicalState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("diagnostic_agent", diagnostic_agent_node)
    builder.add_node("ask_patient", ask_patient_node)
    builder.add_node("physician_review", physician_review_node)
    builder.add_node("report_agent", report_agent_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "FINISH": END,
        },
    )
    builder.add_conditional_edges(
        "diagnostic_agent",
        route_after_diagnostic,
        {"ask_patient": "ask_patient", "supervisor": "supervisor"},
    )
    builder.add_edge("ask_patient", "diagnostic_agent")
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", "supervisor")
    return builder.compile(checkpointer=checkpointer)


# Version sans checkpointer pour LangGraph Studio (il gère la persistance lui-même)
graph = build_graph()
