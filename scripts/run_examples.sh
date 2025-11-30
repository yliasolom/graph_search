#!/bin/bash
# Script to run example usage demos

set -e

echo "=================================="
echo "RAG & Multi-Agent System Examples"
echo "=================================="

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Virtual environment not activated"
    echo "Activate with: source .venv/bin/activate"
    exit 1
fi

# Check environment variables
if [ -z "$OPENAI_API_KEY" ] || [ -z "$NEWS_API_KEY" ]; then
    echo "Error: Missing required API keys"
    echo "Please set OPENAI_API_KEY and NEWS_API_KEY in .env file"
    exit 1
fi

# Run examples
echo ""
echo "Running example usage..."
python examples/example_usage.py

echo ""
echo "Examples completed!"
