"""Lecture des bulles (.context.md) : get_context et search_context.

Le format des bulles est décrit dans CONTEXT-SCHEMA.md.
"""

import os
import re
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_SUFFIX = ".context.md"

# Poids d'un mot trouvé selon l'endroit de la bulle où il apparaît.
WEIGHTS = {"model": 5, "finalite": 3, "columns": 3, "grain": 2, "body": 1}

STOPWORDS = {
    "au", "aux", "avec", "ce", "ces", "comment", "dans", "de", "des", "du", "elle", "en", "est",
    "et", "il", "je", "la", "le", "les", "leur", "mais", "ou", "par", "pas", "pour", "qu", "que",
    "quel", "quelle", "quelles", "quels", "qui", "quoi", "sa", "se", "ses", "son", "sont", "sur",
    "un", "une", "veux", "vs",
}  # fmt: skip


class ContextNotFoundError(LookupError):
    """Aucune bulle n'existe pour le modèle demandé."""


def models_dir() -> Path:
    """Dossier des modèles dbt, surchargeable via CONTEXT_PLATFORM_MODELS_DIR."""
    override = os.environ.get("CONTEXT_PLATFORM_MODELS_DIR")
    if override:
        return Path(override)
    return REPO_ROOT / "dbt_project" / "models"


def _context_files(root: Path | None = None) -> dict[str, Path]:
    root = root or models_dir()
    return {p.name[: -len(CONTEXT_SUFFIX)]: p for p in sorted(root.rglob(f"*{CONTEXT_SUFFIX}"))}


def _split_sections(text: str) -> dict[str, str]:
    """Découpe le markdown sur les titres de niveau 2."""
    sections: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = ""
        elif current is not None:
            sections[current] += line + "\n"
    return {title: body.strip() for title, body in sections.items()}


def _bullet(text: str, label: str) -> str:
    """Valeur d'une puce `- **Label** : valeur`."""
    match = re.search(rf"^\s*-\s*\*\*{label}\*\*\s*:\s*(.*)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _parse_columns(table: str) -> list[dict]:
    """Lit le tableau "Champs attendus" (Champ | Format | Nomenclature | Règles/Tests)."""
    columns = []
    for line in table.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "Champ" or set(cells[0]) <= {"-", ":", " "}:
            continue
        columns.append(
            {
                "name": cells[2].strip("`"),
                "label": cells[0],
                "format": cells[1],
                # Une règle peut contenir un `|` : on recolle ce qui dépasse.
                "rules": " | ".join(cells[3:]),
            }
        )
    return columns


def _display_path(path: Path) -> str:
    """Chemin relatif au repo quand c'est possible, pour rester portable."""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _parse(model: str, path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    sections = _split_sections(text)
    objectifs = sections.get("Objectifs", "")
    return {
        "model": model,
        "layer": path.parent.name,
        "path": _display_path(path),
        "finalite": _bullet(objectifs, "Finalité"),
        "grain": _bullet(objectifs, "Grain"),
        "sections": sections,
        "columns": _parse_columns(sections.get("Champs attendus", "")),
    }


def get_context(model: str, root: Path | None = None) -> dict:
    """Bulle structurée d'un modèle : sections markdown + colonnes.

    Lève ContextNotFoundError si le modèle n'a pas de bulle.
    """
    files = _context_files(root)
    if model not in files:
        raise ContextNotFoundError(
            f"Aucune bulle pour '{model}'. Modèles disponibles : {', '.join(files)}"
        )
    return _parse(model, files[model])


def _normalize(text: str) -> str:
    """Minuscules sans accents, pour chercher 'annee' comme 'année'."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", _normalize(text))


def _keywords(query: str) -> list[str]:
    words = [w for w in _tokens(query) if w not in STOPWORDS and len(w) > 1]
    return list(dict.fromkeys(words))


def _matches(keyword: str, words: set[str]) -> bool:
    """Égalité, ou préfixe commun pour absorber les pluriels (victoire/victoires)."""
    if keyword in words:
        return True
    if len(keyword) < 4:
        return False
    return any(w.startswith(keyword) or (len(w) >= 4 and keyword.startswith(w)) for w in words)


def _excerpts(text: str, keywords: list[str], limit: int = 3) -> list[str]:
    """Lignes de la bulle qui contiennent le plus de mots-clés."""
    scored = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or set(stripped) <= {"|", "-", " ", ":"}:
            continue
        words = set(_tokens(stripped))
        hits = sum(_matches(k, words) for k in keywords)
        if hits:
            scored.append((hits, stripped))
    scored.sort(key=lambda item: -item[0])
    return [line for _, line in scored[:limit]]


def search_context(query: str, limit: int = 5, root: Path | None = None) -> list[dict]:
    """Bulles les plus pertinentes pour une requête, par mots-clés (sans embeddings).

    Retourne des résumés triés par score décroissant ; appeler get_context pour le détail.
    """
    keywords = _keywords(query)
    if not keywords:
        return []

    results = []
    for model, path in _context_files(root).items():
        context = _parse(model, path)
        text = path.read_text(encoding="utf-8")
        fields = {
            "model": set(_tokens(model)),
            "finalite": set(_tokens(context["finalite"])),
            "grain": set(_tokens(context["grain"])),
            "columns": {
                t for c in context["columns"] for t in _tokens(f"{c['name']} {c['label']}")
            },
            "body": set(_tokens(text)),
        }
        matched = [k for k in keywords if _matches(k, fields["body"] | fields["model"])]
        if not matched:
            continue
        score = sum(
            weight
            for k in matched
            for field, weight in WEIGHTS.items()
            if _matches(k, fields[field])
        )
        results.append(
            {
                "model": model,
                "layer": context["layer"],
                "score": score,
                "finalite": context["finalite"],
                "grain": context["grain"],
                "matched_keywords": matched,
                "excerpts": _excerpts(text, matched),
            }
        )

    results.sort(key=lambda r: (-r["score"], r["model"]))
    return results[:limit]
