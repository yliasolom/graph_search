"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import (
    health_router,
    vector_rag_router,
    graph_rag_router,
    agent_router
)
from src.core.config import init_settings
from src.core.logger import log


# Initialize settings
settings = init_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    log.info("Starting RAG & Multi-Agent Analysis API")
    log.info(f"API running on {settings.api_host}:{settings.api_port}")
    log.info(f"Workers: {os.getenv('WEB_CONCURRENCY', '1')}")
    log.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    yield
    
    # Shutdown
    log.info("Shutting down RAG & Multi-Agent Analysis API")


# Create FastAPI app with lifespan
app = FastAPI(
    title="RAG & Multi-Agent Analysis API",
    description="API for Vector RAG, Graph RAG, and Multi-Agent News Analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health_router)
app.include_router(vector_rag_router)
app.include_router(graph_rag_router)
app.include_router(agent_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG & Multi-Agent Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "workers": os.getenv("WEB_CONCURRENCY", "1")
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
