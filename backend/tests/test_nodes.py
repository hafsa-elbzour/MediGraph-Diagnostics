import asyncio

import pytest
from langgraph.checkpoint.memory import MemorySaver

from app import llm
from app.graph import build_graph, route_after_diagnostic
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.report_agent import report_agent_node
from app.state import DISCLAIMER, MAX_QUESTIONS


def test_diagnostic_prepares_question_before_five_answers():
    result = asyncio.run(diagnostic_agent_node({"patient_case": "toux", "question_count": 2}))
    assert result == {"current_question": "Réponse simulée"}


def test_diagnostic_builds_summary_after_five_answers():
    state = {
        "patient_case": "douleur thoracique",
        "question_count": MAX_QUESTIONS,
        "questions_asked": ["q"] * 5,
        "patient_answers": ["r"] * 5,
    }
    result = asyncio.run(diagnostic_agent_node(state))
    assert result["diagnostic_summary"]
    assert result["interim_care"]
    assert result["red_flags"] == ["douleur thoracique"]


def test_report_contains_mandatory_disclaimer():
    state = {
        "patient_case": "toux",
        "diagnostic_summary": "s",
        "interim_care": "c",
        "physician_treatment": "repos",
    }
    result = asyncio.run(report_agent_node(state))
    assert DISCLAIMER in result["final_report"]


def test_route_after_diagnostic():
    assert route_after_diagnostic({"diagnostic_summary": "s"}) == "supervisor"
    assert route_after_diagnostic({"current_question": "q"}) == "ask_patient"


def test_llm_error_is_raised(monkeypatch):
    def broken():
        raise llm.LLMError("clé absente")

    monkeypatch.setattr(llm, "get_llm", broken)
    with pytest.raises(llm.LLMError):
        asyncio.run(diagnostic_agent_node({"patient_case": "toux"}))


def test_graph_has_expected_nodes():
    nodes = set(build_graph(MemorySaver()).get_graph().nodes)
    assert {"supervisor", "diagnostic_agent", "ask_patient",
            "physician_review", "report_agent"} <= nodes
