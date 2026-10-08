"""API FastAPI : expose le graphe LangGraph au frontend."""
import uuid

from fastapi import FastAPI, HTTPException
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.graph import build_graph
from app.llm import LLMError

app = FastAPI(title="Orientation clinique simulée (LangGraph)")
graph = build_graph(MemorySaver())
sessions: set[str] = set()


class StartRequest(BaseModel):
    thread_id: str
    patient_case: str = Field(min_length=3)


class ResumeRequest(BaseModel):
    thread_id: str
    value: str = Field(min_length=1)


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


async def _status(thread_id: str) -> dict:
    """Résume l'état du graphe : où il en est et ce qu'il attend."""
    snapshot = await graph.aget_state(_config(thread_id))
    values = snapshot.values
    if not values:
        raise HTTPException(404, "Consultation introuvable")

    pending = None
    for task in snapshot.tasks:
        if task.interrupts:
            pending = task.interrupts[0].value
    if pending is None:
        status = "completed" if not snapshot.next else "running"
    elif pending["type"] == "patient_question":
        status = "waiting_patient"
    else:
        status = "waiting_physician"

    return {
        "thread_id": thread_id,
        "status": status,
        "question": pending["question"] if status == "waiting_patient" else None,
        "question_count": values.get("question_count", 0),
        "red_flags": values.get("red_flags", []),
        "diagnostic_summary": values.get("diagnostic_summary"),
        "interim_care": values.get("interim_care"),
        "physician_treatment": values.get("physician_treatment"),
        "final_report": values.get("final_report"),
    }


async def _run(payload, thread_id: str) -> dict:
    try:
        await graph.ainvoke(payload, _config(thread_id))
    except LLMError as exc:
        raise HTTPException(502, str(exc)) from exc
    return await _status(thread_id)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/sessions/start")
async def start_session():
    thread_id = str(uuid.uuid4())
    sessions.add(thread_id)
    return {"thread_id": thread_id}


@app.post("/consultation/start")
async def start_consultation(req: StartRequest):
    if req.thread_id not in sessions:
        raise HTTPException(404, "Session inconnue : appelle d'abord /sessions/start")
    if (await graph.aget_state(_config(req.thread_id))).values:
        raise HTTPException(409, "Consultation déjà démarrée")
    return await _run({"patient_case": req.patient_case}, req.thread_id)


@app.post("/consultation/resume")
async def resume_consultation(req: ResumeRequest):
    current = await _status(req.thread_id)
    if current["status"] not in ("waiting_patient", "waiting_physician"):
        raise HTTPException(409, "Aucune réponse n'est attendue pour cette consultation")
    return await _run(Command(resume=req.value), req.thread_id)


@app.get("/consultation/{thread_id}")
async def get_consultation(thread_id: str):
    return await _status(thread_id)


@app.get("/consultation/{thread_id}/report")
async def get_report(thread_id: str):
    status = await _status(thread_id)
    if status["status"] != "completed":
        raise HTTPException(409, "Le rapport n'est pas encore disponible")
    return {"thread_id": thread_id, "final_report": status["final_report"]}
