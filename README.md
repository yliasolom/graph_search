# RAG & Multi-Agent Analysis System

A system for retrieving and analyzing news articles using RAG (Retrieval-Augmented Generation) and multi-agent workflows. The system supports two RAG approaches: vector-based semantic search and graph-based knowledge retrieval. It also includes a multi-agent system that automatically collects, analyzes, and summarizes news on any topic.

## Features

- **Vector RAG**: FAISS-based semantic search with OpenAI embeddings
- **Graph RAG**: Neo4j knowledge graphs for structured retrieval
- **Multi-Agent System**: LangGraph workflow for news analysis
- **REST API**: FastAPI

## Multi-Agent System

The system uses a LangGraph workflow with three sequential agents:

1. **Research Agent**: Fetches news articles from NewsAPI based on the query
2. **Analysis Agent**: Analyzes each article for sentiment, importance, and key facts
3. **Summary Agent**: Generates a final comprehensive report

The workflow handles errors gracefully and processes articles sequentially through the pipeline.

## Quick Start

### Setup

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run locally

```bash
# Start API
python -m src.api.main

# Or use make
make run

# Start Streamlit Web Interface
streamlit run streamlit_app.py
```

## Usage

### API Examples

Build vector database:
```bash
curl -X POST http://localhost:8000/rag/vector/build \
  -H "Content-Type: application/json" \
  -d '{"queries": ["AI news"], "page_size": 5}'
```

Query:
```bash
curl -X POST http://localhost:8000/rag/vector/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest AI trends?"}'
```

News analysis:
```bash
curl -X POST http://localhost:8000/agent/news-analysis \
  -H "Content-Type: application/json" \
  -d '{"query": "climate change"}'
```

Graph RAG:
```bash
# Build graph database
curl -X POST http://localhost:8000/rag/graph/build \
  -H "Content-Type: application/json" \
  -d '{"news_queries": ["AI news"], "page_size": 5}'

# Query graph RAG
curl -X POST http://localhost:8000/rag/graph/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest AI trends?"}'
```

### Python Usage

```python
from src.rag.vector_rag import VectorRAG

rag = VectorRAG()
rag.fetch_and_build(["AI news"], page_size=5)
answer = rag.query("What are the latest AI trends?")
```

## Project Structure

```
graph_search/
├── src/
│   ├── agents/      # Multi-agent systems
│   ├── rag/         # Vector RAG
│   ├── graph/       # Graph RAG
│   ├── api/         # FastAPI app
│   └── core/        # Config & utils
├── tests/           # Unit & integration tests
├── examples/        # Usage examples
└── scripts/         # Utility scripts
```

## Development

```bash
# Run tests
make test

# Format code
make format

# Type check
make type-check

# See all commands
make help
```

## Configuration

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key
- `NEWS_API_KEY` - NewsAPI key
- `NEO4J_URI` - Neo4j connection (default: bolt://localhost:7687)
- `NEO4J_PASSWORD` - Neo4j password

See `.env.example` for all options.

## API Endpoints

- `GET /health` - Health check
- `POST /rag/vector/build` - Build vector database
- `POST /rag/vector/query` - Query vector RAG
- `POST /rag/graph/build` - Build graph database
- `POST /rag/graph/query` - Query graph RAG
- `POST /agent/news-analysis` - Run news analysis

## Tech Stack

- LangChain, LangGraph
- OpenAI
- FAISS
- Neo4j
- FastAPI
