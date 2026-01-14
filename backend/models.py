"""
LLM client models and protocols.
Provides a Protocol for type compatibility across different LLM providers.
"""

import asyncio
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
# OpenAI Implementation with API Key Rotation
# =============================================================================

class OpenAIKeyManager:
    """
    Manages multiple OpenAI API keys with automatic rotation on rate limits.
    
    Usage in .env:
        OPENAI_API_KEY=sk-key1,sk-key2,sk-key3
    
    Keys are rotated when rate limits (429) are hit.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.api_keys = config.OPENAI_API_KEYS.copy()
        self.current_index = 0
        self.rate_limited_keys: Dict[str, float] = {}  # key -> timestamp when rate limited
        self.cooldown_seconds = 60.0  # How long to wait before trying a rate-limited key again
        
        if not self.api_keys:
            raise ValueError("OPENAI_API_KEY is required. Set one or more comma-separated keys.")
        
        print(f"[OpenAI] Initialized with {len(self.api_keys)} API key(s)")
    
    def get_current_key(self) -> str:
        """Get the current active API key."""
        return self.api_keys[self.current_index]
    
    def rotate_key(self, reason: str = "rate limit") -> bool:
        """
        Rotate to the next available API key.
        Returns True if successfully rotated, False if all keys are exhausted.
        """
        import time
        current_time = time.time()
        
        # Mark current key as rate-limited
        current_key = self.api_keys[self.current_index]
        self.rate_limited_keys[current_key] = current_time
        
        # Try to find an available key
        original_index = self.current_index
        attempts = 0
        
        while attempts < len(self.api_keys):
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            next_key = self.api_keys[self.current_index]
            
            # Check if this key is still in cooldown
            if next_key in self.rate_limited_keys:
                time_since_limit = current_time - self.rate_limited_keys[next_key]
                if time_since_limit < self.cooldown_seconds:
                    attempts += 1
                    continue
                else:
                    # Cooldown expired, remove from rate-limited set
                    del self.rate_limited_keys[next_key]
            
            # Found an available key
            key_num = self.current_index + 1
            print(f"[OpenAI] 🔄 Rotated to API key #{key_num}/{len(self.api_keys)} ({reason})")
            return True
        
        # All keys are rate-limited
        self.current_index = original_index  # Reset to original
        return False
    
    def reset_key_status(self, key: str):
        """Mark a key as available again after successful use."""
        if key in self.rate_limited_keys:
            del self.rate_limited_keys[key]


class OpenAILLMClient:
    """OpenAI-compatible LLM client with automatic API key rotation."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        # If explicit key provided, use it. Otherwise use key manager for rotation.
        self._explicit_key = api_key
        self.base_url = base_url or config.OPENAI_BASE_URL
        
        if api_key:
            self._key_manager = None
        else:
            self._key_manager = OpenAIKeyManager()
    
    def _get_api_key(self) -> str:
        """Get the current API key (from manager or explicit)."""
        if self._explicit_key:
            return self._explicit_key
        return self._key_manager.get_current_key()

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
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Use longer timeout for complex extraction tasks (5 minutes)
        timeout = httpx.Timeout(300.0, connect=30.0)
        
        # Retry logic with exponential backoff + key rotation
        max_retries_per_key = 2  # Try each key twice before rotating
        base_delay = 3.0
        total_attempts = 0
        max_total_attempts = len(config.OPENAI_API_KEYS) * max_retries_per_key * 2  # Safety limit
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            while total_attempts < max_total_attempts:
                api_key = self._get_api_key()
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions", headers=headers, json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                    choice = data["choices"][0]["message"]["content"]
                    
                    # Success - mark key as good
                    if self._key_manager:
                        self._key_manager.reset_key_status(api_key)
                    
                    return choice
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        total_attempts += 1
                        
                        # Try to rotate to another key first
                        if self._key_manager and self._key_manager.rotate_key("429 rate limit"):
                            # Successfully rotated - try immediately with new key
                            continue
                        
                        # No rotation available (single key or all exhausted)
                        # Wait with exponential backoff
                        if total_attempts < max_total_attempts:
                            delay = min(base_delay * (2 ** (total_attempts - 1)), 60)
                            key_info = f" (key #{self._key_manager.current_index + 1})" if self._key_manager else ""
                            print(f"[OpenAI] Rate limited{key_info}. Waiting {delay:.0f}s...")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            num_keys = len(config.OPENAI_API_KEYS)
                            raise RuntimeError(
                                f"OpenAI API rate limit exceeded on all {num_keys} key(s). "
                                "All API keys are rate-limited. Wait 5-10 minutes and try again, "
                                "or add more API keys to .env (comma-separated)."
                            )
                    else:
                        # Other HTTP errors - don't retry
                        raise
                        
                except httpx.ReadTimeout:
                    raise RuntimeError(
                        f"OpenAI API request timed out after 300 seconds. "
                        "The document may be too large. Try reducing the document size."
                    )
        
        raise RuntimeError("Failed to get response from OpenAI API after all retries")


class OpenAIEmbeddingClient:
    """OpenAI-compatible embedding client with API key rotation."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._explicit_key = api_key
        self.base_url = base_url or config.OPENAI_BASE_URL
        self.model = model or config.EMBEDDING_MODEL
        
        if api_key:
            self._key_manager = None
        else:
            self._key_manager = OpenAIKeyManager()
    
    def _get_api_key(self) -> str:
        """Get the current API key (from manager or explicit)."""
        if self._explicit_key:
            return self._explicit_key
        return self._key_manager.get_current_key()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using OpenAI embeddings endpoint with key rotation."""
        import time
        
        payload: Dict[str, Any] = {"model": self.model, "input": texts}
        
        # Retry logic with key rotation
        max_retries_per_key = 2
        base_delay = 3.0
        total_attempts = 0
        max_total_attempts = len(config.OPENAI_API_KEYS) * max_retries_per_key * 2
        
        with httpx.Client(timeout=120.0) as client:
            while total_attempts < max_total_attempts:
                api_key = self._get_api_key()
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                
                try:
                    response = client.post(
                        f"{self.base_url}/embeddings",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Success - mark key as good
                    if self._key_manager:
                        self._key_manager.reset_key_status(api_key)
                    
                    return [item["embedding"] for item in data["data"]]
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        total_attempts += 1
                        
                        # Try to rotate to another key first
                        if self._key_manager and self._key_manager.rotate_key("429 rate limit (embeddings)"):
                            # Successfully rotated - try immediately with new key
                            continue
                        
                        # No rotation available - wait with backoff
                        if total_attempts < max_total_attempts:
                            delay = min(base_delay * (2 ** (total_attempts - 1)), 60)
                            key_info = f" (key #{self._key_manager.current_index + 1})" if self._key_manager else ""
                            print(f"[OpenAI Embeddings] Rate limited{key_info}. Waiting {delay:.0f}s...")
                            time.sleep(delay)
                            continue
                        else:
                            num_keys = len(config.OPENAI_API_KEYS)
                            raise RuntimeError(
                                f"OpenAI Embeddings rate limit exceeded on all {num_keys} key(s). "
                                "Wait 5-10 minutes and try again, or add more API keys."
                            )
                    else:
                        raise
        
        raise RuntimeError("Failed to get embeddings from OpenAI API after all retries")


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




