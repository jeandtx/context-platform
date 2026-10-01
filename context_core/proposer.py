"""propose_change : demande en langage naturel -> bulles modifiées -> SQL -> diff.

Deux appels LLM, enchaînés :
1. édition des bulles (.context.md) à partir de la demande ;
2. génération du SQL et de l'entrée schema.yml de chaque bulle modifiée, avec le prompt de
   l'agent sql-regenerator.

Rien n'est écrit dans dbt_project/ : la proposition est enregistrée dans un fichier JSON
(`proposals_dir()`), que validate_change et open_pr relisent pour l'appliquer.
"""

import difflib
import json
import os
import re
import textwrap
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import yaml

from context_core import llm, prompts, reader

CANDIDATES = 5  # bulles ramenées par la recherche, avant ajout de leurs voisines
SQL_WORKERS = 4
MODEL_NAME = re.compile(r"^(?:dim|fact|kpi|stg)_[a-z0-9_]+$")
MODEL_REF = re.compile(r"\b(?:raw|stg|dim|fact|kpi)_[a-z0-9_]+\b")
DBT_REF = re.compile(r"""ref\(\s*['"]([^'"]+)['"]\s*\)""")

EDITOR_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "questions": {"type": "array", "items": {"type": "string"}},
        "bubbles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "model": {"type": "string"},
                    "action": {"type": "string", "enum": ["update", "create"]},
                    "content": {"type": "string"},
                },
                "required": ["model", "action", "content"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "questions", "bubbles"],
    "additionalProperties": False,
}

SQL_SCHEMA = {
    "type": "object",
    "properties": {
        "sql": {"type": "string"},
        "schema_entry": {"type": "string"},
        "bugs_fixed": {"type": "array", "items": {"type": "string"}},
        "decisions": {"type": "array", "items": {"type": "string"}},
        "unresolved": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["sql", "schema_entry", "bugs_fixed", "decisions", "unresolved"],
    "additionalProperties": False,
}


class ProposalError(RuntimeError):
    """La demande n'a pas pu être transformée en proposition exploitable."""


def proposals_dir() -> Path:
    """Dossier des propositions, surchargeable via CONTEXT_PLATFORM_PROPOSALS_DIR."""
    override = os.environ.get("CONTEXT_PLATFORM_PROPOSALS_DIR")
    if override:
        return Path(override)
    return reader.REPO_ROOT / ".context_platform" / "proposals"


def _layer_of(model: str) -> str:
    return "staging" if model.startswith(("raw_", "stg_")) else "marts"


def _references(text: str, known: set[str], exclude: str) -> list[str]:
    names = dict.fromkeys(MODEL_REF.findall(text))
    return [n for n in names if n in known and n != exclude]


def _children(model: str, texts: dict[str, str]) -> list[str]:
    known = set(texts)
    return [m for m, t in texts.items() if m != model and model in _references(t, known, m)]


def _select_models(request: str, texts: dict[str, str]) -> list[str]:
    """Bulles montrées en entier au LLM : résultats de recherche et leurs voisines."""
    hits = [r["model"] for r in reader.search_context(request, limit=CANDIDATES)]
    if not hits:
        return list(texts)
    selected = dict.fromkeys(hits)
    for model in hits:
        for neighbour in [*_references(texts[model], set(texts), model), *_children(model, texts)]:
            selected.setdefault(neighbour)
    return list(selected)


def _editor_message(
    request: str, files: dict[str, Path], texts: dict[str, str], selected: list[str]
) -> str:
    index, lineage, bubbles = [], [], []
    for model, path in files.items():
        ctx = reader._parse(model, path)
        index.append(f"- {model} ({ctx['layer']}) : {ctx['finalite']} | Grain : {ctx['grain']}")
    for model in selected:
        parents = _references(texts[model], set(texts), model)
        lineage.append(f"- {model} : parents={parents}, enfants={_children(model, texts)}")
        bubbles.append(f'<bubble model="{model}">\n{texts[model].strip()}\n</bubble>')
    return (
        f"<request>\n{request}\n</request>\n\n"
        "<models_index>\n" + "\n".join(index) + "\n</models_index>\n\n"
        "<lineage>\n" + "\n".join(lineage) + "\n</lineage>\n\n"
        "<bubbles>\n" + "\n\n".join(bubbles) + "\n</bubbles>"
    )


def _validate_bubble(model: str, content: str, expected_sections: list[str] | None) -> str:
    """Contrôle la forme d'une bulle renvoyée par le LLM ; retourne le texte normalisé."""
    content = content.strip() + "\n"
    if content.splitlines()[0].strip() != f"# Contexte Métier — {model}":
        raise ProposalError(f"Bulle {model} : titre attendu '# Contexte Métier — {model}'.")
    sections = reader._split_sections(content)
    if expected_sections is not None and list(sections) != expected_sections:
        raise ProposalError(
            f"Bulle {model} : sections {list(sections)}, attendu {expected_sections}."
        )
    if not reader._parse_columns(sections.get("Champs attendus", "")):
        raise ProposalError(f"Bulle {model} : tableau 'Champs attendus' vide ou illisible.")
    return content


def _check_bubbles(items: list[dict], texts: dict[str, str], selected: list[str]) -> dict[str, str]:
    """Contrôle les bulles proposées ; retourne {modèle: nouveau contenu} des bulles réellement modifiées."""
    new: dict[str, str] = {}
    for item in items:
        model, action = item["model"], item["action"]
        if model in new:
            raise ProposalError(f"Bulle {model} renvoyée deux fois.")
        if action == "update":
            if model not in selected:
                raise ProposalError(f"Bulle {model} modifiée sans avoir été fournie au modèle.")
            expected = list(reader._split_sections(texts[model]))
        else:
            if not MODEL_NAME.match(model) or model in texts:
                raise ProposalError(f"Création de '{model}' refusée : nom invalide ou déjà pris.")
            expected = None
        content = _validate_bubble(model, item["content"], expected)
        if action == "create" or content != texts[model].strip() + "\n":
            new[model] = content
    return new


def _sql_files() -> dict[str, Path]:
    return {p.stem: p for p in sorted(reader.models_dir().rglob("*.sql"))}


def _sql_message(model: str, bubbles: dict[str, str], sql_files: dict[str, Path]) -> str:
    known = set(bubbles) | set(sql_files)
    upstream, upstream_sql = [], []
    for parent in _references(bubbles[model], known, model):
        if parent in bubbles:
            upstream.append(f'<bubble model="{parent}">\n{bubbles[parent].strip()}\n</bubble>')
        else:
            sql = sql_files[parent].read_text(encoding="utf-8").strip()
            upstream_sql.append(f'<sql model="{parent}">\n{sql}\n</sql>')
    current = sql_files.get(model)
    current_sql = current.read_text(encoding="utf-8").strip() if current else "(new model)"
    return (
        f"Regenerate the dbt model: {model}\n\n"
        f"<context>\n{bubbles[model].strip()}\n</context>\n\n"
        "<upstream>\n" + "\n\n".join(upstream) + "\n</upstream>\n\n"
        "<upstream_sql>\n" + "\n\n".join(upstream_sql) + "\n</upstream_sql>\n\n"
        f"<current_sql>\n{current_sql}\n</current_sql>"
    )


def _generate_sql(model: str, bubbles: dict[str, str], sql_files: dict[str, Path]) -> dict:
    result = llm.complete_json(
        prompts.sql_system(model), _sql_message(model, bubbles, sql_files), SQL_SCHEMA
    )
    sql = result["sql"].strip()
    if not sql:
        raise ProposalError(f"SQL vide pour {model}.")
    unknown = set(DBT_REF.findall(sql)) - set(bubbles) - set(sql_files)
    if unknown:
        raise ProposalError(f"SQL de {model} : ref() vers des modèles inconnus {sorted(unknown)}.")
    result["sql"] = sql + "\n"
    return result


def merge_schema_entry(schema_text: str, model: str, entry: str) -> str:
    """Remplace (ou ajoute) l'entrée d'un modèle dans un schema.yml, en gardant le reste intact."""
    entry = textwrap.dedent(entry).strip("\n")
    try:
        parsed = yaml.safe_load(entry)
    except yaml.YAMLError as exc:
        raise ProposalError(f"schema.yml de {model} : YAML invalide ({exc}).") from exc
    if not (isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict)):
        raise ProposalError(f"schema.yml de {model} : une seule entrée '- name:' attendue.")
    if parsed[0].get("name") != model:
        raise ProposalError(f"schema.yml de {model} : entrée nommée '{parsed[0].get('name')}'.")

    block = textwrap.indent(entry, "  ") + "\n"
    lines = schema_text.splitlines(keepends=True)
    start = next(
        (
            i
            for i, line in enumerate(lines)
            if re.match(rf"^  - name: {re.escape(model)}\s*$", line)
        ),
        None,
    )
    if start is None:
        base = schema_text if schema_text.endswith("\n") else schema_text + "\n"
        return base + "\n" + block
    end = next(
        (i for i in range(start + 1, len(lines)) if re.match(r"^  (?:- name:|#)", lines[i])),
        len(lines),
    )
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1  # les lignes vides avant le bloc suivant restent en place
    return "".join(lines[:start]) + block + "".join(lines[end:])


def _unified_diff(path: str, before: str | None, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            (before or "").splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{path}" if before is not None else "/dev/null",
            tofile=f"b/{path}",
        )
    )


def _new_id() -> str:
    return f"prop-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"


def propose_change(request: str) -> dict:
    """Transforme une demande en langage naturel en bulles modifiées, SQL et diff.

    Retourne {"id", "status", "bulles_modifiees", "sql", "diff", ...}. `status` vaut
    "needs_clarification" (avec `questions`) quand la demande est trop ambiguë pour
    produire un résultat fiable ; aucune proposition n'est alors enregistrée.
    """
    request = request.strip()
    if not request:
        raise ValueError("La demande est vide.")

    files = reader._context_files()
    texts = {model: path.read_text(encoding="utf-8") for model, path in files.items()}
    selected = _select_models(request, texts)

    edit = llm.complete_json(
        prompts.bubble_editor_system(),
        _editor_message(request, files, texts, selected),
        EDITOR_SCHEMA,
    )
    proposal_id = _new_id()
    if edit["questions"] and not edit["bubbles"]:
        return {
            "id": proposal_id,
            "status": "needs_clarification",
            "questions": edit["questions"],
            "summary": edit["summary"],
            "bulles_modifiees": [],
            "sql": "",
            "diff": "",
        }

    new_bubbles = _check_bubbles(edit["bubbles"], texts, selected)
    if not new_bubbles:
        raise ProposalError("Le modèle n'a proposé aucune modification de bulle.")

    # Bulles de référence pour le SQL : version proposée si elle existe, sinon version actuelle.
    all_bubbles = {**texts, **new_bubbles}
    sql_files = _sql_files()
    models = sorted(new_bubbles)
    with ThreadPoolExecutor(max_workers=SQL_WORKERS) as pool:
        results = pool.map(lambda m: _generate_sql(m, all_bubbles, sql_files), models)
        generated = dict(zip(models, results, strict=True))

    changes: dict[str, dict] = {}  # chemin relatif -> {"before": str | None, "after": str}
    schemas: dict[str, tuple[Path, str | None, str]] = {}  # couche -> (chemin, avant, courant)
    for model in models:
        layer = files[model].parent.name if model in files else _layer_of(model)
        directory = files[model].parent if model in files else reader.models_dir() / layer
        bubble_path = files.get(model, directory / f"{model}{reader.CONTEXT_SUFFIX}")
        sql_path = sql_files.get(model, directory / f"{model}.sql")

        for path, after in ((bubble_path, new_bubbles[model]), (sql_path, generated[model]["sql"])):
            before = path.read_text(encoding="utf-8") if path.exists() else None
            if before != after:
                changes[reader._display_path(path)] = {"before": before, "after": after}

        if layer not in schemas:
            schema_path = directory / "schema.yml"
            original = schema_path.read_text(encoding="utf-8") if schema_path.exists() else None
            schemas[layer] = (schema_path, original, original or "version: 2\n\nmodels:\n")
        schema_path, original, current = schemas[layer]
        schemas[layer] = (
            schema_path,
            original,
            merge_schema_entry(current, model, generated[model]["schema_entry"]),
        )
    for schema_path, original, merged in schemas.values():
        if merged != original:
            changes[reader._display_path(schema_path)] = {"before": original, "after": merged}

    diff = "".join(_unified_diff(p, c["before"], c["after"]) for p, c in sorted(changes.items()))
    sql_by_model = {model: generated[model]["sql"] for model in models}
    sql = "\n".join(f"-- {model}.sql\n{text}" for model, text in sql_by_model.items())
    notes = {
        model: {k: generated[model][k] for k in ("bugs_fixed", "decisions", "unresolved")}
        for model in models
    }
    proposal = {
        "id": proposal_id,
        "status": "ready",
        "request": request,
        "summary": edit["summary"],
        "questions": edit["questions"],
        "bulles_modifiees": models,
        "sql": sql,
        "sql_by_model": sql_by_model,
        "diff": diff,
        "files": sorted(changes),
        "notes": notes,
    }
    _save(proposal, changes)
    return proposal


def _save(proposal: dict, changes: dict[str, dict]) -> None:
    """Enregistre la proposition avec le contenu complet des fichiers à écrire."""
    directory = proposals_dir()
    directory.mkdir(parents=True, exist_ok=True)
    stored = {
        **proposal,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "llm_model": llm.model_name(),
        "changes": changes,
    }
    path = directory / f"{proposal['id']}.json"
    path.write_text(json.dumps(stored, ensure_ascii=False, indent=2), encoding="utf-8")
