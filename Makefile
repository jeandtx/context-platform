.PHONY: help install setup lint format test dbt-test dbt-compile dbt-run clean all

help:
	@echo "Available commands:"
	@echo "  make install        Install dependencies with uv"
	@echo "  make setup          Setup pre-commit hooks and environment"
	@echo "  make lint           Run all linters (ruff, sqlfluff)"
	@echo "  make format         Format Python and SQL files"
	@echo "  make test           Run pytest suite"
	@echo "  make dbt-test       Run dbt tests"
	@echo "  make dbt-compile    Compile dbt models (without running)"
	@echo "  make dbt-run        Run dbt pipeline"
	@echo "  make dbt-docs       Generate dbt documentation"
	@echo "  make pre-commit     Run pre-commit hooks manually"
	@echo "  make clean          Clean build artifacts and caches"
	@echo "  make all            Install, setup, lint, format, test, and compile"

install:
	@echo "📦 Installing dependencies with uv..."
	uv sync --all-groups

setup: install
	@echo "🔧 Setting up pre-commit hooks..."
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg
	@echo "✅ Setup complete!"

lint:
	@echo "🔍 Running ruff linter..."
	uv run ruff check . --exclude=dbt_project/target
	@echo "🔍 Running sqlfluff..."
	uv run sqlfluff lint dbt_project/models --dialect duckdb

format:
	@echo "✨ Formatting with ruff..."
	uv run ruff format . --exclude=dbt_project/target
	uv run ruff check . --fix --exclude=dbt_project/target
	@echo "✨ Formatting SQL with sqlfluff..."
	uv run sqlfluff fix dbt_project/models --dialect duckdb

test:
	@echo "🧪 Running pytest..."
	uv run pytest tests/ -v

dbt-parse:
	@echo "🔍 Parsing dbt models..."
	cd dbt_project && uv run dbt parse --profiles-dir ../.dbt

dbt-test:
	@echo "🧪 Running dbt tests..."
	cd dbt_project && uv run dbt test --profiles-dir ../.dbt

dbt-compile:
	@echo "🔨 Compiling dbt models..."
	cd dbt_project && uv run dbt compile --profiles-dir ../.dbt

dbt-run:
	@echo "🚀 Running dbt pipeline..."
	cd dbt_project && uv run dbt run --profiles-dir ../.dbt

dbt-docs:
	@echo "📚 Generating dbt documentation..."
	cd dbt_project && uv run dbt docs generate --profiles-dir ../.dbt

pre-commit:
	@echo "🚨 Running pre-commit hooks on all files..."
	uv run pre-commit run --all-files

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete!"

all: clean setup lint format dbt-compile dbt-test test
	@echo "✅ All checks passed!"
