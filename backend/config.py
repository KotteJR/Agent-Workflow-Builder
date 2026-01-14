"""
Configuration management for the workflow builder backend.
Loads environment variables and provides typed configuration access.
"""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Load .env file
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    """Application configuration loaded from environment variables."""
    
    # LLM Provider
    LLM_PROVIDER: Literal["openai", "ollama", "anthropic"] = os.getenv("LLM_PROVIDER", "openai").lower()  # type: ignore
    
    # OpenAI Configuration
    # Supports multiple API keys (comma-separated) for automatic rotation on rate limits
    # Example: OPENAI_API_KEY=sk-key1,sk-key2,sk-key3
    _OPENAI_API_KEYS_RAW: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_KEYS: list[str] = [k.strip() for k in _OPENAI_API_KEYS_RAW.split(",") if k.strip()]
    OPENAI_API_KEY: str = OPENAI_API_KEYS[0] if OPENAI_API_KEYS else ""  # Primary key for backwards compatibility
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Model Configuration
    SMALL_MODEL: str = os.getenv("SMALL_MODEL", "gpt-4o-mini")
    LARGE_MODEL: str = os.getenv("LARGE_MODEL", "gpt-4o")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # Image Generation
    IMAGE_PROVIDER: Literal["dalle", "gemini", "nano-banana"] = os.getenv("IMAGE_PROVIDER", "nano-banana").lower()  # type: ignore
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_IMAGE_MODEL: str = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")  # Gemini model that supports image generation
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    DOCUMENTS_DIR: Path = BASE_DIR / "documents"
    WORKFLOWS_DIR: Path = BASE_DIR / "workflows"
    EMBEDDINGS_CACHE: Path = BASE_DIR / "embeddings_cache.json"
    
    # Knowledge Base Paths
    LEGAL_DOCUMENTS_DIR: Path = BASE_DIR / "documents" / "legal"
    AUDIT_DOCUMENTS_DIR: Path = BASE_DIR / "documents" / "audit"
    LEGAL_EMBEDDINGS_CACHE: Path = BASE_DIR / "embeddings_cache_legal.json"
    AUDIT_EMBEDDINGS_CACHE: Path = BASE_DIR / "embeddings_cache_audit.json"
    
    @classmethod
    def get_documents_dir(cls, knowledge_base: str = "legal") -> Path:
        """Get the documents directory for the specified knowledge base."""
        if knowledge_base == "audit":
            return cls.AUDIT_DOCUMENTS_DIR
        return cls.LEGAL_DOCUMENTS_DIR
    
    @classmethod
    def get_embeddings_cache(cls, knowledge_base: str = "legal") -> Path:
        """Get the embeddings cache file for the specified knowledge base."""
        if knowledge_base == "audit":
            return cls.AUDIT_EMBEDDINGS_CACHE
        return cls.LEGAL_EMBEDDINGS_CACHE
    
    @classmethod
    def get_model_config(cls) -> dict:
        """Get model configuration based on provider."""
        if cls.LLM_PROVIDER == "ollama":
            return {
                "small": os.getenv("SMALL_MODEL", "llama3.1:8b"),
                "large": os.getenv("LARGE_MODEL", "llama3.1:8b"),
            }
        elif cls.LLM_PROVIDER == "anthropic":
            return {
                "small": os.getenv("SMALL_MODEL", "claude-3-haiku-20240307"),
                "large": os.getenv("LARGE_MODEL", "claude-3-5-sonnet-20241022"),
            }
        else:  # openai
            return {
                "small": cls.SMALL_MODEL,
                "large": cls.LARGE_MODEL,
            }


config = Config()


