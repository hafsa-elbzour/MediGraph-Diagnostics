from types import SimpleNamespace

import pytest

from app import llm
from app.tools import mcp_client


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    """Remplace le vrai LLM : les tests ne font aucun appel réseau."""

    class FakeLLM:
        async def ainvoke(self, messages):
            return SimpleNamespace(content="Réponse simulée")

    monkeypatch.setattr(llm, "get_llm", lambda: FakeLLM())


@pytest.fixture(autouse=True)
def fake_mcp(monkeypatch):
    async def fake_check(text):
        return ["douleur thoracique"] if "thoracique" in text.lower() else []

    monkeypatch.setattr(mcp_client, "check_red_flags", fake_check)
