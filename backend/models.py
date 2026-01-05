"""
LLM client models and protocols.
Provides a Protocol for type compatibility across different LLM providers.
"""

import os
from typing import Any, Dict, List, Protocol, runtime_checkable

import httpx

from config import config


@runtime_checkable
class LLMClientProtocol(Protocol):
    """Protocol defining the interface for LLM clients."""
    
    async def chat(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        """Send a chat completion request and return the response content."""
        ...


@runtime_checkable
class EmbeddingClientProtocol(Protocol):
    """Protocol defining the interface for embedding clients."""
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts and return their embedding vectors."""
        ...


# =============================================================================
# OpenAI Implementation
# =============================================================================

class OpenAILLMClient:
    """OpenAI-compatible LLM client using plain HTTP calls."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or config.OPENAI_API_KEY
        self.base_url = base_url or config.OPENAI_BASE_URL
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")

    async def chat(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]["message"]["content"]
        return choice


class OpenAIEmbeddingClient:
    """OpenAI-compatible embedding client."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or config.OPENAI_API_KEY
        self.base_url = base_url or config.OPENAI_BASE_URL
        self.model = model or config.EMBEDDING_MODEL
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using OpenAI embeddings endpoint."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {"model": self.model, "input": texts}
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        
        return [item["embedding"] for item in data["data"]]


# =============================================================================
# Ollama Implementation
# =============================================================================

class OllamaLLMClient:
    """Ollama-compatible LLM client using the Ollama HTTP API."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or config.OLLAMA_BASE_URL

    async def chat(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{model}' not found. Run: ollama pull {model}"
                ) from e
            raise
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is Ollama running? Start with: ollama serve"
            )

        return data["message"]["content"]


class OllamaEmbeddingClient:
    """Ollama-compatible embedding client."""
    
    MAX_TEXT_LENGTH = 2048

    def __init__(
        self, 
        base_url: str | None = None, 
        model: str | None = None
    ) -> None:
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.OLLAMA_EMBEDDING_MODEL

    def _truncate(self, text: str) -> str:
        if len(text) > self.MAX_TEXT_LENGTH:
            return text[:self.MAX_TEXT_LENGTH]
        return text

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        
        with httpx.Client(timeout=300.0) as client:
            for i, text in enumerate(texts):
                truncated = self._truncate(text)
                payload = {
                    "model": self.model,
                    "input": truncated,
                }
                
                try:
                    response = client.post(
                        f"{self.base_url}/api/embed",
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    embeddings.append(data["embeddings"][0])
                    print(f"[OLLAMA] Embedded document {i+1}/{len(texts)}")
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        raise RuntimeError(
                            f"Ollama model '{self.model}' not found. Run: ollama pull {self.model}"
                        ) from e
                    raise
                except httpx.ConnectError:
                    raise RuntimeError(
                        f"Cannot connect to Ollama at {self.base_url}. "
                        "Is Ollama running? Start with: ollama serve"
                    )
        
        return embeddings


# =============================================================================
# Factory Functions
# =============================================================================

def get_llm_client() -> LLMClientProtocol:
    """Create and return the appropriate LLM client based on LLM_PROVIDER."""
    if config.LLM_PROVIDER == "ollama":
        return OllamaLLMClient()
    else:
        return OpenAILLMClient()


def get_embedding_client() -> EmbeddingClientProtocol:
    """Create and return the appropriate embedding client based on LLM_PROVIDER."""
    if config.LLM_PROVIDER == "ollama":
        return OllamaEmbeddingClient()
    else:
        return OpenAIEmbeddingClient()

