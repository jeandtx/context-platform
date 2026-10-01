"""Stubs du contrat d'interface, utilisés tant que context_core.api n'est pas disponible."""

_MODELS = [
    {
        "name": "kpi_performance_vs_population",
        "layer": "marts",
        "purpose": "KPI de performance sportive rapportée à la population",
        "grain": "une ligne par pays",
    },
]


def list_models() -> list[dict]:
    return _MODELS


def get_context(model: str) -> dict:
    return {"model": model, "sections": {}, "columns": [], "stub": True}


def get_lineage(model: str) -> dict:
    return {"parents": [], "children": [], "stub": True}


def search_context(query: str) -> list[dict]:
    return [m for m in _MODELS if query.lower() in str(m).lower()]


def propose_change(request: str) -> dict:
    return {"id": "stub-1", "bulles_modifiees": [], "sql": "", "diff": "", "request": request}


def validate_change(proposal_id: str) -> dict:
    return {"proposal_id": proposal_id, "status": "stub"}


def open_pr(proposal_id: str) -> str:
    return f"stub-branch-{proposal_id}"


def regenerate(model: str) -> dict:
    return {"model": model, "identical": None, "stub": True}
