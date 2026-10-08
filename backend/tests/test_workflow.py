"""Workflow complet : 5 questions, interruption médecin, rapport final."""
import asyncio

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.graph import build_graph
from app.state import DISCLAIMER


async def _pending(graph, config):
    snapshot = await graph.aget_state(config)
    return snapshot.tasks[0].interrupts[0].value


async def _run_full(case: str):
    graph = build_graph(MemorySaver())
    config = {"configurable": {"thread_id": "t1"}}
    await graph.ainvoke({"patient_case": case}, config)
    for i in range(5):
        assert (await _pending(graph, config))["type"] == "patient_question"
        await graph.ainvoke(Command(resume=f"réponse {i}"), config)
    assert (await _pending(graph, config))["type"] == "physician_review"
    await graph.ainvoke(Command(resume="Repos et hydratation"), config)
    return await graph.aget_state(config)


def test_full_workflow():
    final = asyncio.run(_run_full("Toux et fièvre"))
    assert final.next == ()
    assert final.values["question_count"] == 5
    assert len(final.values["patient_answers"]) == 5
    assert final.values["physician_treatment"] == "Repos et hydratation"
    assert DISCLAIMER in final.values["final_report"]


def test_red_flags_case():
    final = asyncio.run(_run_full("Douleur thoracique brutale"))
    assert final.values["red_flags"] == ["douleur thoracique"]
