"""API routes for the RAG and analysis services."""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from src.api.models import (
    QueryRequest,
    NewsAnalysisRequest,
    BuildVectorDBRequest,
    BuildGraphRequest,
    RAGResponse,
    NewsAnalysisResponse,
    StatusResponse,
    HealthResponse,
    ArticleAnalysis,
    RetrievedDocument
)
from src.rag.vector_rag import VectorRAG
from src.graph.graph_rag import GraphRAG
from src.agents.news_analysis_agent import NewsAnalysisAgent
from src.core.logger import log


# Create routers
health_router = APIRouter(prefix="/health", tags=["Health"])
vector_rag_router = APIRouter(prefix="/rag/vector", tags=["Vector RAG"])
graph_rag_router = APIRouter(prefix="/rag/graph", tags=["Graph RAG"])
agent_router = APIRouter(prefix="/agent", tags=["Multi-Agent"])


# Global instances (in production, use dependency injection)
vector_rag_instance: VectorRAG = None
graph_rag_instance: GraphRAG = None


@health_router.get("/", response_model=HealthResponse)
async def health_check():
    """Check API health and service status."""
    services = {
        "api": "healthy",
        "vector_rag": "initialized" if vector_rag_instance else "not_initialized",
        "graph_rag": "initialized" if graph_rag_instance else "not_initialized"
    }

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services=services
    )


# Vector RAG endpoints
@vector_rag_router.post("/build", response_model=StatusResponse)
async def build_vector_database(request: BuildVectorDBRequest):
    """Build vector database from news articles."""
    global vector_rag_instance

    try:
        log.info(f"Building vector DB with queries: {request.queries}")

        vector_rag_instance = VectorRAG()
        vector_rag_instance.fetch_and_build(
            queries=request.queries,
            page_size=request.page_size
        )

        return StatusResponse(
            status="success",
            message="Vector database built successfully",
            details={
                "queries": request.queries,
                "page_size": request.page_size
            }
        )
    except Exception as e:
        log.error(f"Error building vector DB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build vector database: {str(e)}"
        )


@vector_rag_router.post("/query", response_model=RAGResponse)
async def query_vector_rag(request: QueryRequest):
    """Query the vector RAG system."""
    if vector_rag_instance is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vector database not initialized. Please build it first."
        )

    try:
        log.info(f"Vector RAG query: {request.question}")
        answer, documents, context = vector_rag_instance.query(request.question, k=request.k)

        def build_snippet(text: str, limit: int = 300) -> str:
            """Return a short preview of the chunk content."""
            if len(text) <= limit:
                return text
            return text[:limit].rstrip() + "..."

        retrieved_docs: List[RetrievedDocument] = []
        for doc in documents:
            metadata = doc.metadata or {}
            retrieved_docs.append(
                RetrievedDocument(
                    title=metadata.get("title", "Untitled"),
                    url=metadata.get("url"),
                    snippet=build_snippet(doc.page_content)
                )
            )

        return RAGResponse(
            question=request.question,
            answer=answer,
            context_used=context,
            documents=retrieved_docs
        )
    except Exception as e:
        log.error(f"Error querying vector RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query vector RAG: {str(e)}"
        )


# Graph RAG endpoints
@graph_rag_router.post("/build", response_model=StatusResponse)
async def build_graph_database(request: BuildGraphRequest):
    """Build graph database (knowledge + lexical)."""
    global graph_rag_instance

    try:
        log.info("Building graph database")

        if graph_rag_instance is None:
            graph_rag_instance = GraphRAG()

        if request.start_clean:
            graph_rag_instance.erase_graph()

        if request.leagues:
            graph_rag_instance.build_knowledge_graph(leagues=request.leagues)

        if request.news_queries:
            graph_rag_instance.build_lexical_graph(
                queries=request.news_queries,
                page_size=request.page_size
            )

        return StatusResponse(
            status="success",
            message="Graph database built successfully",
            details={
                "leagues": request.leagues,
                "news_queries": request.news_queries,
                "start_clean": request.start_clean
            }
        )
    except Exception as e:
        log.error(f"Error building graph DB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build graph database: {str(e)}"
        )


@graph_rag_router.post("/query", response_model=RAGResponse)
async def query_graph_rag(request: QueryRequest):
    """Query the graph RAG system."""
    if graph_rag_instance is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Graph database not initialized. Please build it first."
        )

    try:
        log.info(f"Graph RAG query: {request.question}")
        answer = graph_rag_instance.query(request.question)

        return RAGResponse(
            question=request.question,
            answer=answer
        )
    except Exception as e:
        log.error(f"Error querying graph RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query graph RAG: {str(e)}"
        )


# Multi-Agent endpoints
@agent_router.post("/news-analysis", response_model=NewsAnalysisResponse)
async def analyze_news(request: NewsAnalysisRequest):
    """Run multi-agent news analysis."""
    try:
        log.info(f"Starting news analysis for: {request.query}")

        agent = NewsAnalysisAgent()
        result = agent.run(request.query)

        # Convert analysis results to Pydantic models
        analysis_results = []
        for item in result.get("analysis_results", []):
            analysis_results.append(ArticleAnalysis(**item))

        return NewsAnalysisResponse(
            query=result["query"],
            articles_found=len(result.get("articles", [])),
            articles_analyzed=len(result.get("analysis_results", [])),
            analysis_results=analysis_results,
            final_summary=result.get("final_summary", ""),
            error=result.get("error")
        )
    except Exception as e:
        log.error(f"Error in news analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze news: {str(e)}"
        )
