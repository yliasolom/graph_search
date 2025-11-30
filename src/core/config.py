"""Configuration management for the application."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # News API
    news_api_key: str = Field(..., env="NEWS_API_KEY")

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", env="NEO4J_USERNAME")
    neo4j_password: str = Field(..., env="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", env="NEO4J_DATABASE")

    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Scaling
    web_concurrency: int = Field(default=1, env="WEB_CONCURRENCY")
    max_workers: int = Field(default=4, env="MAX_WORKERS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Model Configuration
    default_model: str = Field(default="gpt-4o-mini", env="DEFAULT_MODEL")
    default_temperature: float = Field(default=0.1, env="DEFAULT_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="MAX_TOKENS")

    # RAG Configuration
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    top_k_results: int = Field(default=3, env="TOP_K_RESULTS")

    # News Configuration
    default_news_page_size: int = Field(default=5, env="DEFAULT_NEWS_PAGE_SIZE")
    max_article_length: int = Field(default=3000, env="MAX_ARTICLE_LENGTH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings: Optional[Settings] = None


def init_settings() -> Settings:
    """Initialize settings singleton."""
    global settings
    if settings is None:
        settings = get_settings()
    return settings
