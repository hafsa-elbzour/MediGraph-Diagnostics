from fastapi.testclient import TestClient

from app import llm
from app.api import app

client = TestClient(app)


def _start(case="Toux et fièvre"):
    thread_id = client.post("/sessions/start").json()["thread_id"]
    response = client.post(
        "/consultation/start", json={"thread_id": thread_id, "patient_case": case}
    )
    return thread_id, response


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_full_consultation_through_api():
    thread_id, response = _start()
    data = response.json()
    for i in range(5):
        assert data["status"] == "waiting_patient"
        assert data["question"]
        data = client.post(
            "/consultation/resume", json={"thread_id": thread_id, "value": f"r{i}"}
        ).json()
    assert data["status"] == "waiting_physician"
    assert data["diagnostic_summary"] and data["interim_care"]

    data = client.post(
        "/consultation/resume", json={"thread_id": thread_id, "value": "Repos"}
    ).json()
    assert data["status"] == "completed"

    report = client.get(f"/consultation/{thread_id}/report").json()
    assert "ne remplace pas une consultation médicale" in report["final_report"]


def test_report_not_ready_returns_409():
    thread_id, _ = _start()
    assert client.get(f"/consultation/{thread_id}/report").status_code == 409


def test_unknown_session_and_consultation():
    body = {"thread_id": "inconnu", "patient_case": "toux"}
    assert client.post("/consultation/start", json=body).status_code == 404
    assert client.get("/consultation/inconnu").status_code == 404


def test_empty_answer_is_rejected():
    thread_id, _ = _start()
    response = client.post("/consultation/resume", json={"thread_id": thread_id, "value": ""})
    assert response.status_code == 422


def test_llm_error_returns_502(monkeypatch):
    def broken():
        raise llm.LLMError("clé absente")

    monkeypatch.setattr(llm, "get_llm", broken)
    _, response = _start()
    assert response.status_code == 502
