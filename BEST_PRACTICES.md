# Best Practices Guide

This document outlines the best practices implemented in the context-platform project.

## 🏗️ Project Structure

The project follows a modular structure with clear separation of concerns:

```
context-platform/
├── dbt_project/              # dbt models and tests
│   ├── models/
│   │   ├── staging/          # Raw data transformations (views)
│   │   └── marts/            # Business-ready tables (tables)
│   ├── tests/                # dbt tests and assertions
│   └── macros/               # Reusable dbt logic
├── scripts/                  # Utility scripts
├── tests/                    # Python unit tests
├── .dbt/                     # dbt configuration
├── .github/                  # GitHub configuration and workflows
└── Makefile                  # Development commands
```

## 🔧 Development Tools

### Package Management: `uv`

We use `uv` for fast, reliable Python package management:

```bash
uv sync --all-groups          # Install all dependencies
uv pip install package-name   # Add new packages
```

**Why uv?**
- ⚡ 10-100x faster than pip
- 🔒 Deterministic builds (via `uv.lock`)
- 🎯 Simple, focused CLI

### Code Formatting: `ruff`

Ruff handles Python linting, formatting, and import sorting:

```bash
make format   # Auto-format all Python files
make lint     # Check for linting issues
```

**Config:** `ruff.toml` and `[tool.ruff]` in `pyproject.toml`

**Why ruff?**
- ⚡ Fast (written in Rust)
- 📦 All-in-one tool (replaces black, isort, flake8)
- 🎯 Sensible defaults

### SQL Linting: `sqlfluff`

SQLFluff validates and formats SQL code:

```bash
uv run sqlfluff lint dbt_project/models --dialect duckdb
uv run sqlfluff fix dbt_project/models --dialect duckdb
```

**Config:** `.sqlfluff`

**Why sqlfluff?**
- 📝 SQL-specific rules
- 🎯 dbt template support
- 💪 DuckDB dialect support

### Git Hooks: `pre-commit`

Pre-commit hooks run automatically before committing:

```bash
make pre-commit              # Run all hooks manually
uv run pre-commit install    # Install hooks
```

**Hooks include:**
- Ruff (Python linting/formatting)
- SQLFluff (SQL linting)
- YAML/JSON validation
- Detect secrets
- File formatting (prettier)

## 🧪 Testing Strategy

### Python Unit Tests

```bash
make test              # Run all tests with coverage
```

**Location:** `tests/` directory
**Framework:** pytest
**Coverage target:** >80%

### dbt Tests

```bash
make dbt-test          # Run dbt tests
make dbt-compile       # Validate model compilation
```

**Types:**
- **Uniqueness tests** — Check for duplicate keys
- **NOT NULL tests** — Ensure required fields exist
- **Referential integrity** — Validate foreign keys
- **Custom tests** — Business logic validation

### CI/CD Pipeline

GitHub Actions runs all tests on every PR:

1. **Linting** — Code style and formatting
2. **Security** — Secret detection
3. **dbt validation** — Model compilation and tests
4. **Unit tests** — Python test suite
5. **Coverage** — Code coverage reporting

**Workflow:** `.github/workflows/ci.yml`

## 📚 Documentation Standards

### dbt Model Documentation

Each model should have:

1. **YAML definition** (`schema.yml`)
   - Column descriptions
   - Data tests
   - Configuration options

2. **Context file** (`[model_name].context.md`)
   - Business purpose
   - Grain and scope
   - Transformations applied
   - Expected fields
   - Data quality rules

**Example structure:**
```
dbt_project/models/marts/
├── dim_customers.sql
├── dim_customers.yml
└── dim_customers.context.md
```

### Code Documentation

- **Docstrings** — Functions and modules
- **Comments** — Complex logic
- **Type hints** — Function signatures
- **README** — Project overview

## 🔐 Security Best Practices

### Secret Management

- ❌ Never commit secrets
- ✅ Use environment variables (`.env` files locally)
- ✅ Pre-commit hook detects secrets
- ✅ Scan before committing: `detect-secrets scan`

### SQL Injection Prevention

- ✅ Always use parameterized queries
- ✅ Use dbt templating for dynamic SQL
- ✅ Never concatenate user input directly

### Code Review

- All PRs require review before merging
- Use CODEOWNERS for automated assignments
- Check for security issues in review

## 🚀 Performance Optimization

### dbt Performance

1. **Incremental models** — Update only new/changed data
2. **Materialization strategy** — Views vs tables
3. **Indexing** — Primary keys on dimension tables
4. **Partitioning** — Large fact tables (if applicable)

### SQL Query Optimization

1. **Avoid SELECT \*** — Only select needed columns
2. **Use WHERE clauses** — Filter early
3. **Denormalize when needed** — Balance normalization vs performance
4. **Monitor query logs** — Identify slow queries

### Python Performance

1. **Vectorization** — Use pandas/numpy operations
2. **Lazy evaluation** — Process data in chunks
3. **Caching** — Cache expensive computations
4. **Profiling** — Use `pytest-benchmark` for slow functions

## 📋 Naming Conventions

### dbt Models

- `stg_[source]_[entity]` — Staging models (raw transformations)
- `dim_[entity]` — Dimension tables
- `fct_[process]` — Fact tables
- `kpi_[metric]` — KPI tables
- `rpt_[report]` — Report tables

**Examples:**
- `stg_salesforce_accounts`
- `dim_customers`
- `fct_orders`
- `kpi_monthly_revenue`

### Columns

- Descriptive names: `customer_id`, not `cust_id`
- Consistent naming: `created_at`, `updated_at`
- Type prefixes (optional): `is_active`, `count_orders`
- Timestamps: `_at` for datetime (e.g., `created_at`)
- Dates: `_date` for dates only (e.g., `birth_date`)

### Branches

- `feat/feature-name` — New features
- `fix/bug-name` — Bug fixes
- `refactor/change-name` — Code refactoring
- `docs/topic` — Documentation updates

## 📝 Commit Message Standards

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code refactoring
- `docs` — Documentation
- `test` — Test additions
- `chore` — Build, tooling, dependencies
- `perf` — Performance improvement

**Example:**
```
feat(models): add customer lifetime value metric

- Calculate LTV using 12-month rolling average
- Add validation tests for LTV accuracy
- Update documentation with calculation logic

Closes #123
```

## 🔄 Release Process

1. **Feature branch** → `develop` (PR with review)
2. **Release candidate** → version bump
3. **Tag release** → `main` with semantic versioning
4. **Document changes** → CHANGELOG.md

**Versioning:** Semantic versioning (MAJOR.MINOR.PATCH)

## 🎓 Learning Resources

- **dbt:** https://docs.getdbt.com
- **Ruff:** https://docs.astral.sh/ruff/
- **SQLFluff:** https://docs.sqlfluff.com
- **Conventional Commits:** https://www.conventionalcommits.org/

## ✅ Quick Checklist

Before committing:

- [ ] Code formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Tests pass (`make test`)
- [ ] dbt compiles (`make dbt-compile`)
- [ ] dbt tests pass (`make dbt-test`)
- [ ] No secrets committed
- [ ] Documentation updated
- [ ] Commit message follows conventions

---

**Questions?** See `CONTRIBUTING.md` or open an issue!
