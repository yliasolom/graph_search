"""Utility functions for fetching news and articles."""
import re
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup
from readability import Document
from requests.adapters import HTTPAdapter
from trafilatura import extract as trafilatura_extract
from urllib3.util import Retry

from src.core.config import init_settings
from src.core.logger import log


settings = init_settings()

_NOISE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"see all",
        r"daily digest",
        r"all rights reserved",
        r"this is the title for the native ad",
        r"subscribe",
        r"sign up",
    ]
]

_SESSION = requests.Session()
_retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=_retry)
_SESSION.mount("http://", adapter)
_SESSION.mount("https://", adapter)
_SESSION.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
)


def _html_to_text(html: str) -> str:
    """Convert HTML snippet to normalized plain text."""
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _filter_paragraphs(paragraphs: List[str]) -> List[str]:
    """Remove navigation/ads and very short segments."""
    filtered: List[str] = []
    seen: set[str] = set()

    for p in paragraphs:
        text = re.sub(r"\s+", " ", p).strip()
        lower = text.lower()

        if not text or len(text) < 80:
            continue
        if any(pattern.search(lower) for pattern in _NOISE_PATTERNS):
            continue
        if lower in seen:
            continue

        filtered.append(text)
        seen.add(lower)

    return filtered


def fetch_article_text(url: str, max_chars: int = None) -> Optional[str]:
    """
    Fetch and clean full article text from a news URL.

    Args:
        url: Article URL to fetch
        max_chars: Maximum characters to return (default from settings)

    Returns:
        Extracted article text or None if failed
    """
    if max_chars is None:
        max_chars = settings.max_article_length

    try:
        resp = _SESSION.get(url, timeout=15)
        resp.raise_for_status()
        html = resp.text

        candidates: List[str] = []

        # Attempt readability-based extraction for main content.
        try:
            doc = Document(html)
            candidates.append(_html_to_text(doc.summary(html_partial=True)))
        except Exception as parse_err:
            log.debug(f"Readability parse failed for {url}: {parse_err}")

        soup = BeautifulSoup(html, "html.parser")

        # Trafilatura sometimes extracts better text for complex pages
        try:
            trafilatura_text = trafilatura_extract(
                html,
                include_comments=False,
                include_tables=False,
                favor_precision=True,
            )
            if trafilatura_text:
                candidates.append(_html_to_text(trafilatura_text))
        except Exception as trafilatura_err:
            log.debug(f"Trafilatura parse failed for {url}: {trafilatura_err}")

        # Fall back to <article> tag content
        article_tag = soup.find("article")
        if article_tag:
            candidates.append(_html_to_text(str(article_tag)))

        # Last resort: filtered paragraphs
        paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
        filtered_paragraphs = _filter_paragraphs(paragraphs)
        if filtered_paragraphs:
            candidates.append(" ".join(filtered_paragraphs))

        # Choose the longest reasonable candidate
        candidates = [c for c in candidates if c]
        if not candidates:
            return None

        best_text = max(candidates, key=len)
        return best_text[:max_chars]
    except Exception as e:
        log.warning(f"Could not fetch article text from {url}: {e}")
        return None


def fetch_article(article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Fetch full article with text content.

    Args:
        article: Article metadata dictionary

    Returns:
        Complete article dictionary with text content
    """
    title = article.get("title", "")
    url = article.get("url", "")
    author = article.get("author", "")
    description = article.get("description", "")
    published_at = article.get("publishedAt", "")
    content = article.get("content", "")

    text = fetch_article_text(url)
    if not text:
        log.warning(f"Skipping article without text: {url or title}")
        return None

    return {
        "title": title,
        "url": url,
        "author": author,
        "description": description,
        "publishedAt": published_at,
        "content": content,
        "text": text
    }


def fetch_teams(league: str) -> List[Dict[str, Any]]:
    """
    Fetch sports teams from TheSportsDB API.

    Args:
        league: League name (e.g., "NBA", "NHL")

    Returns:
        List of team dictionaries
    """
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l={league}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        teams = data.get("teams") or []
        return teams
    except Exception as e:
        log.error(f"Error fetching teams for {league}: {e}")
        return []


def fetch_news(query: str, page_size: int = None) -> List[Dict[str, Any]]:
    """
    Fetch news articles from NewsAPI.

    Args:
        query: Search query
        page_size: Number of articles to fetch (default from settings)

    Returns:
        List of article dictionaries
    """
    if page_size is None:
        page_size = settings.default_news_page_size

    try:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={settings.news_api_key}&pageSize={page_size}&language=en"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "ok":
            articles = data.get("articles") or []
            return articles
        else:
            log.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        log.error(f"Error fetching news for query '{query}': {e}")
        return []
