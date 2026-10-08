"""Serveur MCP : expose l'outil `check_red_flags` (détection de signaux d'alerte)."""
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clinical-tools")
DATA_FILE = Path(__file__).parent / "data" / "red_flags.json"


@mcp.tool()
def check_red_flags(text: str) -> str:
    """Cherche des signaux d'alerte dans un texte. Retourne une liste JSON."""
    flags = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    lowered = text.lower()
    return json.dumps([f for f in flags if f in lowered], ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()  # transport stdio
