#!/bin/bash
# Setup script for context-platform development environment
set -e

echo "🚀 Setting up context-platform development environment..."

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.10 or later."
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "⚠️  uv is not installed. Installing uv..."
    pip install uv
fi

echo "✅ Python and uv are available"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --all-groups

# Setup pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Initialize dbt
echo "🔨 Initializing dbt..."
cd dbt_project
uv run dbt parse --profiles-dir ../.dbt
cd ..

# Run checks
echo "🔍 Running initial checks..."
make lint
make dbt-compile

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  • Run 'make help' to see available commands"
echo "  • Run 'make dbt-run' to execute the dbt pipeline"
echo "  • Run 'make all' to run all tests and checks"
