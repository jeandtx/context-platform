"""Vérifie que le serveur MCP expose le contrat d'interface et que les stubs le respectent."""

import asyncio
import json
import os

os.environ["CONTEXT_CORE_STUBS"] = "1"

from mcp_server.server import mcp  # noqa: E402

CONTRACT = {
    "list_models": {},
    "get_context": {"model": "kpi_performance_vs_population"},
    "get_lineage": {"model": "kpi_performance_vs_population"},
    "search_context": {"query": "population"},
    "propose_change": {"request": "victoires par million d'habitants"},
    "validate_change": {"proposal_id": "stub-1"},
    "open_pr": {"proposal_id": "stub-1"},
    "regenerate": {"model": "kpi_performance_vs_population"},
}


def _call(name, args):
    """Renvoie le résultat de l'outil, que le SDK le donne structuré ou en texte."""
    result = asyncio.run(mcp.call_tool(name, args))
    if isinstance(result, tuple):
        structured = result[1]
        return structured["result"] if set(structured) == {"result"} else structured
    return json.loads(result[0].text)


def test_expose_les_8_outils_du_contrat():
    tools = asyncio.run(mcp.list_tools())
    assert {t.name for t in tools} == set(CONTRACT)


def test_chaque_outil_est_documente():
    for tool in asyncio.run(mcp.list_tools()):
        assert tool.description, f"{tool.name} sans description (l'agent en a besoin)"


def test_list_models_renvoie_nom_couche_finalite_grain():
    models = _call("list_models", {})
    assert models
    assert {"name", "layer", "purpose", "grain"} <= set(models[0])


def test_get_lineage_renvoie_parents_et_enfants():
    lineage = _call("get_lineage", CONTRACT["get_lineage"])
    assert {"parents", "children"} <= set(lineage)


def test_propose_change_renvoie_un_id_et_un_diff():
    proposal = _call("propose_change", CONTRACT["propose_change"])
    assert {"id", "bulles_modifiees", "sql", "diff"} <= set(proposal)


def test_tous_les_resultats_sont_serialisables_en_json():
    for name, args in CONTRACT.items():
        json.dumps(_call(name, args))
