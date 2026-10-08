"""Client MCP : appelle l'outil `check_red_flags` exposé par mcp_server/server.py."""
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DEFAULT_SERVER = Path(__file__).resolve().parents[3] / "mcp_server" / "server.py"


class MCPError(Exception):
    pass


async def check_red_flags(text: str) -> list[str]:
    """Retourne la liste des signaux d'alerte trouvés dans le texte."""
    server_path = os.getenv("MCP_SERVER_PATH", str(DEFAULT_SERVER))
    params = StdioServerParameters(command=sys.executable, args=[server_path])
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("check_red_flags", {"text": text})
        return json.loads(result.content[0].text)
    except Exception as exc:
        raise MCPError(f"Appel MCP impossible : {exc}") from exc
