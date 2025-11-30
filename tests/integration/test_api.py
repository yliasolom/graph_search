"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from src.api.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data


class TestVectorRAGEndpoints:
    """Tests for Vector RAG endpoints."""

    @patch('src.api.routes.VectorRAG')
    def test_build_vector_database(self, mock_rag):
        """Test building vector database."""
        mock_instance = Mock()
        mock_rag.return_value = mock_instance

        response = client.post(
            "/rag/vector/build",
            json={
                "queries": ["test query"],
                "page_size": 3
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_query_without_build(self):
        """Test querying without building database first."""
        response = client.post(
            "/rag/vector/query",
            json={
                "question": "test question"
            }
        )

        assert response.status_code == 400
        assert "not initialized" in response.json()["detail"].lower()


class TestGraphRAGEndpoints:
    """Tests for Graph RAG endpoints."""

    @patch('src.api.routes.GraphRAG')
    def test_build_graph_database(self, mock_graph):
        """Test building graph database."""
        mock_instance = Mock()
        mock_graph.return_value = mock_instance

        response = client.post(
            "/rag/graph/build",
            json={
                "leagues": ["NBA"],
                "news_queries": ["NBA news"],
                "page_size": 5,
                "start_clean": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestAgentEndpoints:
    """Tests for multi-agent endpoints."""

    @patch('src.api.routes.NewsAnalysisAgent')
    def test_news_analysis(self, mock_agent):
        """Test news analysis endpoint."""
        mock_instance = Mock()
        mock_instance.run.return_value = {
            "query": "test",
            "articles": [{"title": "Test"}],
            "analysis_results": [{
                "article_title": "Test",
                "topic": "Tech",
                "sentiment": "positive",
                "key_facts": ["fact1"],
                "importance": 8,
                "source": "TestSource"
            }],
            "final_summary": "Test summary",
            "error": None
        }
        mock_agent.return_value = mock_instance

        response = client.post(
            "/agent/news-analysis",
            json={"query": "test"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert data["articles_found"] == 1
        assert len(data["analysis_results"]) == 1


class TestValidation:
    """Tests for request validation."""

    def test_invalid_query_empty(self):
        """Test validation with empty query."""
        response = client.post(
            "/agent/news-analysis",
            json={"query": ""}
        )

        assert response.status_code == 422

    def test_invalid_k_parameter(self):
        """Test validation with invalid k parameter."""
        response = client.post(
            "/rag/vector/query",
            json={
                "question": "test",
                "k": 0
            }
        )

        assert response.status_code == 422
