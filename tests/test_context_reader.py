"""Tests de lecture des bulles, sur 3 bulles réelles du projet."""

import pytest

from context_core.reader import ContextNotFoundError, get_context, search_context

SECTIONS = ["Objectifs", "Transformations", "Champs attendus", "Tests de logique métier", "Notes"]


@pytest.mark.parametrize(
    "model,layer,grain,columns",
    [
        (
            "kpi_performance_vs_population",
            "marts",
            "Une ligne par pays unique.",
            ["country_name", "wins", "population_value", "performance_ratio"],
        ),
        (
            "dim_population",
            "marts",
            "Une ligne par combinaison **pays + année**.",
            None,
        ),
        ("stg_matches", "staging", "Une ligne par match unique.", None),
    ],
)
def test_get_context_structure(model, layer, grain, columns):
    context = get_context(model)

    assert context["model"] == model
    assert context["layer"] == layer
    assert context["grain"] == grain
    assert context["finalite"]
    assert list(context["sections"]) == SECTIONS
    assert context["path"] == f"dbt_project/models/{layer}/{model}.context.md"
    assert context["columns"]
    if columns is not None:
        assert [c["name"] for c in context["columns"]] == columns


def test_get_context_columns_detail():
    columns = {c["name"]: c for c in get_context("kpi_performance_vs_population")["columns"]}

    assert columns["performance_ratio"] == {
        "name": "performance_ratio",
        "label": "KPI ratio",
        "format": "Décimal",
        "rules": "Obligatoire, valeur = wins ÷ population, > 0",
    }


def test_get_context_large_table():
    names = [c["name"] for c in get_context("stg_matches")["columns"]]

    assert len(names) == 32
    assert names[0] == "match_id"
    assert names[-1] == "data_version"


def test_get_context_sections_keep_markdown():
    transformations = get_context("dim_population")["sections"]["Transformations"]

    assert transformations.startswith("- **Source**")
    assert "## " not in transformations


def test_get_context_unknown_model():
    with pytest.raises(ContextNotFoundError, match="kpi_performance_vs_population"):
        get_context("modele_inexistant")


def test_search_finds_kpi_from_business_question():
    results = search_context("Que mesure le KPI performance vs population ?")

    assert results[0]["model"] == "kpi_performance_vs_population"
    assert results[0]["excerpts"]
    assert {"model", "layer", "score", "finalite", "grain", "matched_keywords"} <= set(results[0])


def test_search_by_column_name():
    results = search_context("performance_ratio")

    assert results[0]["model"] == "kpi_performance_vs_population"
    assert results[0]["score"] > results[1]["score"]


def test_search_ignores_accents_and_plurals():
    with_accents = [r["model"] for r in search_context("année de population")]
    without = [r["model"] for r in search_context("annees de populations")]

    assert with_accents == without
    assert "dim_population" in with_accents[:2]


def test_search_sorted_and_limited():
    results = search_context("pays", limit=3)

    assert len(results) == 3
    assert [r["score"] for r in results] == sorted((r["score"] for r in results), reverse=True)


@pytest.mark.parametrize("query", ["", "le la de", "zzzxqw"])
def test_search_no_result(query):
    assert search_context(query) == []


def test_models_dir_override(tmp_path, monkeypatch):
    bubble = tmp_path / "marts" / "dim_demo.context.md"
    bubble.parent.mkdir()
    bubble.write_text(
        "# Contexte Métier — dim_demo\n\n## Objectifs\n\n- **Finalité** : Démo.\n"
        "- **Grain** : Une ligne par démo.\n\n## Champs attendus\n\n"
        "| Champ | Format | Nomenclature | Règles/Tests |\n| --- | --- | --- | --- |\n"
        "| Identifiant | Entier | `demo_id` | Obligatoire |\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTEXT_PLATFORM_MODELS_DIR", str(tmp_path))

    context = get_context("dim_demo")

    assert context["finalite"] == "Démo."
    assert context["columns"] == [
        {"name": "demo_id", "label": "Identifiant", "format": "Entier", "rules": "Obligatoire"}
    ]
    assert [r["model"] for r in search_context("demo")] == ["dim_demo"]
