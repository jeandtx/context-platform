"""Contrat d'interface de context_core, consommé par le serveur MCP et la webapp."""

from context_core.proposer import propose_change
from context_core.reader import get_context, search_context

__all__ = ["get_context", "propose_change", "search_context"]
