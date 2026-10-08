import asyncio
import importlib
import sys

import pytest

pytest.importorskip("mcp")


def test_real_mcp_server_detects_red_flags(monkeypatch):
    """Test d'intégration : lance vraiment le serveur MCP (sans le faux client)."""
    from app.tools import mcp_client

    importlib.reload(mcp_client)  # annule le monkeypatch du conftest
    flags = asyncio.run(mcp_client.check_red_flags("Douleur thoracique depuis ce matin"))
    assert "douleur thoracique" in flags
    assert sys.executable
