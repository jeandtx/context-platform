# Contributing to Context Platform

Thank you for contributing to the context-platform project! This document provides guidelines and instructions for development.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `uv` (ultra-fast Python package installer)
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/jeandtx/context-platform.git
cd context-platform

# Run the setup script
./scripts/setup.sh

# Or manually:
uv sync --all-groups
uv run pre-commit install
```

## 📋 Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work (never commit to `main`):

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feat/` — new features
- `fix/` — bug fixes
- `refactor/` — code refactoring
- `docs/` — documentation updates
- `test/` — test improvements
- `chore/` — maintenance tasks

### 2. Make Your Changes

While working, follow these guidelines:

#### Code Quality

```bash
# Check for linting issues
make lint

# Auto-format code
make format

# Run tests
make test
```

#### dbt Models

```bash
# Validate dbt models
make dbt-compile

# Run dbt tests
make dbt-test

# Run the full pipeline
make dbt-run
```

#### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. They include:

- **Ruff** — Python linting and formatting
- **SQLFluff** — SQL linting
- **YAML/JSON validation** — Config file checks
- **Security checks** — Detect secrets

To run them manually:

```bash
make pre-commit
```

### 3. Testing

Ensure all tests pass before submitting a PR:

```bash
# Run all tests
make all

# Or individually:
make test          # Unit tests
make dbt-test      # dbt tests
make dbt-compile   # Model compilation
make lint          # Linting
```

### 4. Commit & Push

```bash
git add .
git commit -m "feat: add new feature"
git push origin feat/your-feature-name
```

Commit message conventions (conventional commits):

- `feat:` — new features
- `fix:` — bug fixes
- `docs:` — documentation
- `test:` — test changes
- `refactor:` — code refactoring
- `perf:` — performance improvements
- `chore:` — build, tooling, dependencies

### 5. Create a Pull Request

Open a PR on GitHub with:

- Clear title and description
- Link to any related issues
- Screenshots/dbt docs if relevant
- Checklist of what you've tested

## 🧪 Testing Guidelines

### Python Tests

```bash
uv run pytest tests/ -v
```

### dbt Tests

```bash
cd dbt_project
uv run dbt test --profiles-dir ../.dbt
```

Tests should cover:

- Model logic and transformations
- Data quality (uniqueness, nullability, etc.)
- Business rule validation

### Coverage

Aim for >80% test coverage:

```bash
make test  # Generates coverage report in htmlcov/
```

## 📚 Documentation

- **dbt models** — Document in `[model_name].context.md` files
- **README** — Keep main README updated
- **Code comments** — Add comments for complex logic
- **Changelog** — Document breaking changes

## 🔍 Code Review Checklist

Before submitting a PR, verify:

- [ ] Branch created from `main` or `develop`
- [ ] All tests pass locally (`make all`)
- [ ] Code is formatted (`make format`)
- [ ] No linting errors (`make lint`)
- [ ] dbt models compile (`make dbt-compile`)
- [ ] dbt tests pass (`make dbt-test`)
- [ ] No secrets committed (checked by pre-commit)
- [ ] Documentation updated
- [ ] Commit messages follow conventions

## 🐛 Bug Reports

When reporting bugs, include:

- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment (Python version, OS, etc.)
- Screenshots/logs if applicable

## 💡 Feature Requests

Feature requests should include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if applicable)
- Alternative approaches (if applicable)

## 📦 Dependency Management

We use `uv` for fast, reliable dependency management.

### Adding Dependencies

```bash
# Development dependency
uv pip install --dev package-name

# Production dependency
uv pip install package-name

# Update lock file
uv sync
```

Then commit the updated `uv.lock`.

## 🔐 Security

- Never commit secrets or credentials
- Use `.env` files locally (add to `.gitignore`)
- Don't store passwords in code
- Review for SQL injection or other vulnerabilities

## 📖 Useful Commands

```bash
# Quick help
make help

# Full setup and checks
make all

# Specific checks
make lint          # Linting only
make format        # Format code
make test          # Run tests
make dbt-compile   # Compile dbt
make dbt-test      # Test dbt
make clean         # Clean artifacts
```

## 🆘 Getting Help

- Check existing issues/PRs
- Read the main README
- Review dbt documentation: https://docs.getdbt.com
- Reach out in discussions or issues

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Happy coding! 🎉
