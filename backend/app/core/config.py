"""Project Atlas Application Configuration."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Atlas - AI Research Copilot"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security & API Auth
    API_KEY: str = "atlas-secret-key-2025"
    API_KEY_HEADER_NAME: str = "X-API-Key"
    
    # Database Configuration
    DATABASE_URL: str = "mysql+pymysql://atlas_user:atlas_pass@localhost:3306/atlas_db"
    READ_ONLY_DATABASE_URL: Optional[str] = None
    SQL_QUERY_TIMEOUT_SECONDS: float = 5.0
    SQL_ROW_LIMIT: int = 50
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "data/vector_db"
    CHROMA_COLLECTION_NAME: str = "market_reports"
    
    # Embedding & LLM Configuration
    EMBEDDING_PROVIDER: str = "chroma_default"  # 'chroma_default', 'sentence_transformers', 'fastembed', 'gemini', 'openai'
    LLM_PROVIDER: str = "deterministic"  # 'deterministic', 'gemini', 'openai', 'ollama'
    
    # LLM API Keys (optional if running in deterministic offline mode)
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gemini-1.5-flash"
    
    # Escalation and Confidence Parameters
    ESCALATION_CONFIDENCE_THRESHOLD: float = 0.70
    REQUEST_TIMEOUT_SECONDS: float = 30.0
    
    # Data directory
    REPORTS_DIR: str = "data/reports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
