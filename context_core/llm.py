"""Appel à l'API Anthropic avec sortie JSON contrainte par un schéma."""

import functools
import json
import os

import anthropic

DEFAULT_MODEL = "claude-opus-5-5"
MAX_TOKENS = 32000


class LLMError(RuntimeError):
    """Réponse inexploitable : refus, troncature ou JSON absent."""


def model_name() -> str:
    """Modèle utilisé, surchargeable via CONTEXT_CORE_MODEL."""
    return os.environ.get("CONTEXT_CORE_MODEL", DEFAULT_MODEL)


@functools.cache
def _client() -> anthropic.Anthropic:
    # Identifiants lus par le SDK : ANTHROPIC_API_KEY ou profil `ant auth login`.
    return anthropic.Anthropic()


def complete_json(system: list[str], user: str, schema: dict, *, effort: str = "high") -> dict:
    """Envoie un prompt et renvoie l'objet JSON conforme à `schema`.

    En streaming : avec la réflexion et un fichier SQL complet en sortie, la réponse peut
    dépasser la durée tolérée par une requête non streamée.
    """
    with _client().messages.stream(
        model=model_name(),
        max_tokens=MAX_TOKENS,
        system=[{"type": "text", "text": block} for block in system],
        messages=[{"role": "user", "content": user}],
        output_config={
            "effort": effort,
            "format": {"type": "json_schema", "schema": schema},
        },
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "refusal":
        raise LLMError("Le modèle a refusé la demande (stop_reason=refusal).")
    if message.stop_reason == "max_tokens":
        raise LLMError(f"Réponse tronquée à {MAX_TOKENS} tokens : demande trop large.")
    text = next((b.text for b in message.content if b.type == "text"), None)
    if text is None:
        raise LLMError("Aucun texte dans la réponse du modèle.")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMError(f"Réponse non conforme au schéma JSON : {exc}") from exc
