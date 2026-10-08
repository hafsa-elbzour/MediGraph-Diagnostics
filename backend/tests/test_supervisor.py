import asyncio

from app.nodes.supervisor import supervisor_node


def nxt(state):
    return asyncio.run(supervisor_node(state))["next"]


def test_supervisor_routes_in_order():
    assert nxt({}) == "diagnostic_agent"
    assert nxt({"diagnostic_summary": "s"}) == "physician_review"
    assert nxt({"diagnostic_summary": "s", "physician_treatment": "t"}) == "report_agent"
    full = {"diagnostic_summary": "s", "physician_treatment": "t", "final_report": "r"}
    assert nxt(full) == "FINISH"
