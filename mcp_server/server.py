"""Serveur MCP (FastMCP) exposant le contrat d'interface de context_core.

Lancement :
    uv run python -m mcp_server.server                 # stdio (Claude Desktop / Claude Code)
    uv run python -m mcp_server.server --http          # streamable-http sur 127.0.0.1:8765/mcp
    CONTEXT_CORE_STUBS=1 pour forcer les stubs.
"""

import os
import sys

from mcp.server.fastmcp import FastMCP

try:
    if os.environ.get("CONTEXT_CORE_STUBS"):
        raise ModuleNotFoundError(name="context_core")
    from context_core import api
except ModuleNotFoundError as exc:
    # Repli sur les stubs uniquement si context_core est absent. Une dépendance
    # manquante à l'intérieur de context_core doit remonter, pas être masquée.
    if exc.name != "context_core":
        raise
    from mcp_server import stubs as api

print(f"[mcp_server] backend: {api.__name__}", file=sys.stderr)

mcp = FastMCP("context-platform", host="127.0.0.1", port=8765)


@mcp.tool()
def list_models() -> list[dict]:
    """Liste les modèles dbt : nom, couche, finalité, grain. À appeler en premier."""
    return api.list_models()


@mcp.tool()
def get_context(model: str) -> dict:
    """Retourne la bulle (contexte métier, colonnes, règles de calcul) d'un modèle."""
    return api.get_context(model)


@mcp.tool()
def get_lineage(model: str) -> dict:
    """Retourne les parents et enfants d'un modèle."""
    return api.get_lineage(model)


@mcp.tool()
def search_context(query: str) -> list[dict]:
    """Recherche par mots-clés dans l'index des bulles."""
    return api.search_context(query)


@mcp.tool()
def propose_change(request: str) -> dict:
    """Transforme une demande en langage naturel en bulles modifiées, SQL et diff."""
    return api.propose_change(request)


@mcp.tool()
def validate_change(proposal_id: str) -> dict:
    """Lance dbt build/test sur la proposition et compare les données à la baseline."""
    return api.validate_change(proposal_id)


@mcp.tool()
def open_pr(proposal_id: str) -> str:
    """Ouvre une PR pour la proposition. Retourne l'URL, ou le nom de branche en repli."""
    return api.open_pr(proposal_id)


@mcp.tool()
def regenerate(model: str) -> dict:
    """Régénère un modèle depuis sa bulle et le compare à la baseline."""
    return api.regenerate(model)


def main() -> None:
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
