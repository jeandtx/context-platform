"""propose_change avec un LLM simulé : orchestration, garde-fous et persistance."""

import json

import pytest

from context_core import llm, prompts, proposer, reader

KPI = "kpi_performance_vs_population"
RATIO_ROW = "| KPI ratio   | Décimal | `performance_ratio` | Obligatoire, valeur = wins ÷ population, > 0                |"
NEW_ROW = "| Victoires par million | Décimal | `wins_per_million` | Obligatoire, = wins ÷ population x 1 000 000 |"
SQL = """{{ config(materialized='table') }}

select
  f.country_name,
  f.wins,
  p.population_value,
  f.wins / p.population_value as performance_ratio,
  f.wins / p.population_value * 1000000 as wins_per_million
from {{ ref('fact_country_performance') }} as f
inner join {{ ref('dim_population') }} as p
  on f.country_name = p.country_name
where p.year = 2023 and p.population_value > 0
"""
ENTRY = """\
- name: kpi_performance_vs_population
  description: KPI de performance rapportée à la population
  columns:
    - name: wins_per_million
      description: Victoires par million d'habitants
      tests:
        - not_null
"""


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTEXT_PLATFORM_PROPOSALS_DIR", str(tmp_path / "proposals"))


def _kpi_with_new_column() -> str:
    text = (reader.models_dir() / "marts" / f"{KPI}.context.md").read_text(encoding="utf-8")
    assert RATIO_ROW in text, "la bulle du KPI a changé : mettre à jour la fixture du test"
    return text.replace(RATIO_ROW, RATIO_ROW + "\n" + NEW_ROW)


class FakeLLM:
    """Répond à l'édition de bulle puis à la génération SQL, et garde les appels."""

    def __init__(self, editor=None, sql=None):
        self.calls = []
        self.editor = editor or {
            "summary": "Ajout d'une colonne.",
            "questions": [],
            "bubbles": [{"model": KPI, "action": "update", "content": _kpi_with_new_column()}],
        }
        self.sql = sql or {
            "sql": SQL,
            "schema_entry": ENTRY,
            "bugs_fixed": ["filtre année 2023"],
            "decisions": [],
            "unresolved": [],
        }

    def __call__(self, system, user, schema, *, effort="high"):
        self.calls.append({"system": system, "user": user, "schema": schema, "effort": effort})
        return self.editor if "bubbles" in schema["properties"] else self.sql


def test_propose_change_contrat_et_diff(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(llm, "complete_json", fake)
    models_dir = reader.models_dir()
    before = (models_dir / "marts" / f"{KPI}.sql").read_text(encoding="utf-8")

    proposal = proposer.propose_change("Ajouter les victoires par million d'habitants au KPI")

    assert {"id", "bulles_modifiees", "sql", "diff"} <= set(proposal)
    json.dumps(proposal)
    assert proposal["status"] == "ready"
    assert proposal["bulles_modifiees"] == [KPI]
    assert "wins_per_million" in proposal["sql"]
    assert f"+{NEW_ROW}" in proposal["diff"]
    assert f"b/dbt_project/models/marts/{KPI}.sql" in proposal["diff"]
    assert "+      - name: wins_per_million" in proposal["diff"]
    assert proposal["notes"][KPI]["bugs_fixed"] == ["filtre année 2023"]
    # La proposition ne touche pas au dépôt.
    assert (models_dir / "marts" / f"{KPI}.sql").read_text(encoding="utf-8") == before


def test_propose_change_enregistre_la_proposition(monkeypatch, tmp_path):
    monkeypatch.setattr(llm, "complete_json", FakeLLM())

    proposal = proposer.propose_change("Ajouter les victoires par million d'habitants au KPI")

    stored = json.loads((tmp_path / "proposals" / f"{proposal['id']}.json").read_text("utf-8"))
    path = f"dbt_project/models/marts/{KPI}.context.md"
    assert stored["request"].startswith("Ajouter")
    assert "wins_per_million" in stored["changes"][path]["after"]
    assert stored["changes"][path]["before"] == (reader.REPO_ROOT / path).read_text("utf-8")


def test_le_prompt_sql_vient_de_l_agent_sql_regenerator(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(llm, "complete_json", fake)

    proposer.propose_change("Ajouter les victoires par million d'habitants au KPI")

    sql_call = next(c for c in fake.calls if "sql" in c["schema"]["properties"])
    assert sql_call["system"][0] == prompts.regenerator_prompt()
    assert "DuckDB conventions" in sql_call["system"][0]
    assert not sql_call["system"][0].startswith("---")  # frontmatter retiré
    assert f"<context>\n{_kpi_with_new_column().strip()}" in sql_call["user"]
    assert '<bubble model="fact_country_performance">' in sql_call["user"]


def test_l_editeur_recoit_les_bulles_voisines(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(llm, "complete_json", fake)

    proposer.propose_change("Ajouter les victoires par million d'habitants au KPI")

    user = fake.calls[0]["user"]
    assert f'<bubble model="{KPI}">' in user
    assert '<bubble model="fact_country_performance">' in user  # parent
    assert "<models_index>" in user


def test_demande_ambigue_renvoie_des_questions(monkeypatch):
    editor = {"summary": "", "questions": ["Quelle année de population ?"], "bubbles": []}
    fake = FakeLLM(editor=editor)
    monkeypatch.setattr(llm, "complete_json", fake)

    proposal = proposer.propose_change("Améliore le KPI")

    assert proposal["status"] == "needs_clarification"
    assert proposal["questions"] == ["Quelle année de population ?"]
    assert proposal["bulles_modifiees"] == []
    assert len(fake.calls) == 1  # pas de génération SQL


def test_bulle_identique_ne_declenche_aucun_sql(monkeypatch):
    current = (reader.models_dir() / "marts" / f"{KPI}.context.md").read_text(encoding="utf-8")
    editor = {
        "summary": "",
        "questions": [],
        "bubbles": [{"model": KPI, "action": "update", "content": current}],
    }
    monkeypatch.setattr(llm, "complete_json", FakeLLM(editor=editor))

    with pytest.raises(proposer.ProposalError, match="aucune modification"):
        proposer.propose_change("Ajouter les victoires par million d'habitants au KPI")


@pytest.mark.parametrize(
    "bubble,message",
    [
        ({"model": "dim_teams", "action": "update", "content": "x"}, "sans avoir été fournie"),
        ({"model": KPI, "action": "create", "content": "x"}, "refusée"),
        ({"model": "pas un modele", "action": "create", "content": "x"}, "refusée"),
        ({"model": KPI, "action": "update", "content": "# Autre titre\n"}, "titre attendu"),
        (
            {
                "model": KPI,
                "action": "update",
                "content": f"# Contexte Métier — {KPI}\n\n## Notes\n",
            },
            "sections",
        ),
    ],
)
def test_bulles_invalides_rejetees(monkeypatch, bubble, message):
    editor = {"summary": "", "questions": [], "bubbles": [bubble]}
    monkeypatch.setattr(llm, "complete_json", FakeLLM(editor=editor))

    with pytest.raises(proposer.ProposalError, match=message):
        proposer.propose_change("Ajouter les victoires par million d'habitants au KPI")


def test_ref_vers_un_modele_inconnu_rejete(monkeypatch):
    sql = {
        "sql": "select * from {{ ref('dim_inconnue') }}",
        "schema_entry": ENTRY,
        "bugs_fixed": [],
        "decisions": [],
        "unresolved": [],
    }
    monkeypatch.setattr(llm, "complete_json", FakeLLM(sql=sql))

    with pytest.raises(proposer.ProposalError, match="dim_inconnue"):
        proposer.propose_change("Ajouter les victoires par million d'habitants au KPI")


def test_demande_vide():
    with pytest.raises(ValueError):
        proposer.propose_change("   ")


SCHEMA = """\
version: 2

models:
  # A
  - name: dim_a
    description: a
    columns:
      - name: x

  # B
  - name: dim_b
    description: b
"""


def test_merge_schema_remplace_une_entree_et_garde_le_reste():
    merged = proposer.merge_schema_entry(SCHEMA, "dim_a", "- name: dim_a\n  description: nouveau\n")

    assert "  - name: dim_a\n    description: nouveau\n\n  # B\n  - name: dim_b" in merged
    assert "columns:" not in merged.split("# B")[0]


def test_merge_schema_ajoute_une_entree_manquante():
    merged = proposer.merge_schema_entry(SCHEMA, "dim_c", "- name: dim_c\n  description: c\n")

    assert merged.startswith(SCHEMA)
    assert merged.endswith("\n  - name: dim_c\n    description: c\n")


def test_merge_schema_dernier_bloc():
    merged = proposer.merge_schema_entry(SCHEMA, "dim_b", "- name: dim_b\n  description: z\n")

    assert merged.endswith("  - name: dim_b\n    description: z\n")


@pytest.mark.parametrize(
    "entry", ["- name: autre\n", "name: dim_a\n", "- name: dim_a\n- name: dim_b\n", "- name: [\n"]
)
def test_merge_schema_entree_invalide(entry):
    with pytest.raises(proposer.ProposalError):
        proposer.merge_schema_entry(SCHEMA, "dim_a", entry)
