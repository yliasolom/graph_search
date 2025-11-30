#!/bin/bash
# Development environment setup script

set -e

echo "=================================="
echo "Setting up development environment"
echo "=================================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install pre-commit hooks
echo ""
echo "Installing pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs data/raw data/processed data/vector_stores models

echo ""
echo "=================================="
echo "Development environment ready!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start Neo4j: make neo4j-start"
echo "3. Run tests: make test"
echo "4. Start API: make run"
echo ""
