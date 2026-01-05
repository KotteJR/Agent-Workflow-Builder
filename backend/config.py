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
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Model Configuration
    SMALL_MODEL: str = os.getenv("SMALL_MODEL", "gpt-4o-mini")
    LARGE_MODEL: str = os.getenv("LARGE_MODEL", "gpt-4o")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # Image Generation
    IMAGE_PROVIDER: Literal["dalle", "gemini"] = os.getenv("IMAGE_PROVIDER", "dalle").lower()  # type: ignore
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    DOCUMENTS_DIR: Path = BASE_DIR / "documents"
    WORKFLOWS_DIR: Path = BASE_DIR / "workflows"
    EMBEDDINGS_CACHE: Path = BASE_DIR / "embeddings_cache.json"
    
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


