"""Unit tests for utility functions."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.utils import fetch_article_text, fetch_article, fetch_teams, fetch_news


class TestFetchArticleText:
    """Tests for fetch_article_text function."""

    @patch('src.core.utils.requests.get')
    def test_fetch_article_text_success(self, mock_get):
        """Test successful article text fetching."""
        mock_response = Mock()
        mock_response.text = "<html><body><p>Test paragraph 1</p><p>Test paragraph 2</p></body></html>"
        mock_get.return_value = mock_response

        result = fetch_article_text("https://example.com/article")

        assert result is not None
        assert "Test paragraph 1" in result
        assert "Test paragraph 2" in result

    @patch('src.core.utils.requests.get')
    def test_fetch_article_text_failure(self, mock_get):
        """Test article text fetching with exception."""
        mock_get.side_effect = Exception("Connection error")

        result = fetch_article_text("https://example.com/article")

        assert result is None

    @patch('src.core.utils.requests.get')
    def test_fetch_article_text_max_chars(self, mock_get):
        """Test article text truncation."""
        long_text = "a" * 5000
        mock_response = Mock()
        mock_response.text = f"<html><body><p>{long_text}</p></body></html>"
        mock_get.return_value = mock_response

        result = fetch_article_text("https://example.com/article", max_chars=100)

        assert result is not None
        assert len(result) == 100


class TestFetchArticle:
    """Tests for fetch_article function."""

    @patch('src.core.utils.fetch_article_text')
    def test_fetch_article_with_text(self, mock_fetch_text):
        """Test fetching article with successful text extraction."""
        mock_fetch_text.return_value = "Full article text content"

        article_input = {
            "title": "Test Title",
            "url": "https://example.com",
            "author": "Test Author",
            "description": "Test Description",
            "publishedAt": "2024-01-01",
            "content": "Short content"
        }

        result = fetch_article(article_input)

        assert result["title"] == "Test Title"
        assert result["text"] == "Full article text content"
        assert result["author"] == "Test Author"

    @patch('src.core.utils.fetch_article_text')
    def test_fetch_article_without_text(self, mock_fetch_text):
        """Test fetching article when text extraction fails."""
        mock_fetch_text.return_value = None

        article_input = {
            "title": "Test Title",
            "url": "https://example.com",
            "description": "Test Description",
            "publishedAt": "2024-01-01"
        }

        result = fetch_article(article_input)

        assert result["text"] == "Test Title Test Description"


class TestFetchTeams:
    """Tests for fetch_teams function."""

    @patch('src.core.utils.requests.get')
    def test_fetch_teams_success(self, mock_get):
        """Test successful team fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "teams": [
                {"idTeam": "1", "strTeam": "Team 1"},
                {"idTeam": "2", "strTeam": "Team 2"}
            ]
        }
        mock_get.return_value = mock_response

        result = fetch_teams("NBA")

        assert len(result) == 2
        assert result[0]["strTeam"] == "Team 1"

    @patch('src.core.utils.requests.get')
    def test_fetch_teams_failure(self, mock_get):
        """Test team fetching with exception."""
        mock_get.side_effect = Exception("API error")

        result = fetch_teams("NBA")

        assert result == []


class TestFetchNews:
    """Tests for fetch_news function."""

    @patch('src.core.utils.requests.get')
    def test_fetch_news_success(self, mock_get):
        """Test successful news fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {"title": "Article 1", "url": "https://example.com/1"},
                {"title": "Article 2", "url": "https://example.com/2"}
            ]
        }
        mock_get.return_value = mock_response

        result = fetch_news("test query", page_size=2)

        assert len(result) == 2
        assert result[0]["title"] == "Article 1"

    @patch('src.core.utils.requests.get')
    def test_fetch_news_api_error(self, mock_get):
        """Test news fetching with API error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "error",
            "message": "API limit reached"
        }
        mock_get.return_value = mock_response

        result = fetch_news("test query")

        assert result == []
