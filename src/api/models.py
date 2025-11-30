"""Pydantic models for API request/response validation."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    question: str = Field(..., description="Question to answer", min_length=1)
    k: Optional[int] = Field(None, description="Number of documents to retrieve", ge=1, le=10)


class NewsAnalysisRequest(BaseModel):
    """Request model for news analysis."""
    query: str = Field(..., description="Search query for news", min_length=1)


class BuildVectorDBRequest(BaseModel):
    """Request model for building vector database."""
    queries: List[str] = Field(..., description="List of search queries", min_items=1)
    page_size: Optional[int] = Field(3, description="Articles per query", ge=1, le=20)


class BuildGraphRequest(BaseModel):
    """Request model for building graph database."""
    leagues: Optional[List[str]] = Field(None, description="List of leagues for knowledge graph")
    news_queries: Optional[List[str]] = Field(None, description="Queries for lexical graph")
    page_size: Optional[int] = Field(10, description="Articles per query", ge=1, le=20)
    start_clean: Optional[bool] = Field(False, description="Erase existing graph")


class ArticleAnalysis(BaseModel):
    """Model for individual article analysis."""
    article_title: str
    topic: str
    sentiment: str
    key_facts: List[str]
    importance: int
    source: Optional[str] = None


class NewsAnalysisResponse(BaseModel):
    """Response model for news analysis."""
    query: str
    articles_found: int
    articles_analyzed: int
    analysis_results: List[ArticleAnalysis]
    final_summary: str
    error: Optional[str] = None


class RetrievedDocument(BaseModel):
    """Metadata returned with vector search results."""
    title: str
    url: Optional[str] = None
    snippet: str


class RAGResponse(BaseModel):
    """Response model for RAG queries."""
    question: str
    answer: str
    context_used: Optional[str] = None
    documents: List[RetrievedDocument] = Field(default_factory=list)


class StatusResponse(BaseModel):
    """Response model for status checks."""
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response model for health checks."""
    status: str
    version: str
    services: Dict[str, str]
