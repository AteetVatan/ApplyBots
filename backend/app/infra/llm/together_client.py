"""Together AI LLM client implementation.

Standards: python_clean.mdc
- Async HTTP with httpx
- Retry with tenacity
- Proper error handling
"""

from typing import AsyncIterator

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.ports.llm import LLMMessage, LLMResponse

logger = structlog.get_logger(__name__)

# Default embedding model
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"


class TogetherAPIError(Exception):
    """Together AI API error."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"Together AI API error ({status_code}): {message}")


class TogetherLLMClient:
    """Together AI LLM client implementation.

    Implements the LLMClient protocol for Together AI's OpenAI-compatible API.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.together.xyz/v1",
        timeout: float = 120.0,
    ) -> None:
        """Initialize the Together AI client.

        Args:
            api_key: Together AI API key
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def complete(
        self,
        *,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a completion.

        Args:
            messages: List of chat messages
            model: Model identifier (e.g., "meta-llama/Llama-3.3-70B-Instruct-Turbo")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with generated content and usage stats

        Raises:
            TogetherAPIError: If API request fails
        """
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        logger.debug(
            "llm_complete_request",
            model=model,
            message_count=len(messages),
            temperature=temperature,
            max_tokens=max_tokens,
        )

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )

            if response.status_code != 200:
                error_detail = response.text
                logger.error(
                    "llm_complete_error",
                    status_code=response.status_code,
                    error=error_detail,
                )
                raise TogetherAPIError(response.status_code, error_detail)

            data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        logger.info(
            "llm_complete_success",
            model=model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )

        return LLMResponse(
            content=content,
            model=model,
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
        )

    async def stream(
        self,
        *,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Stream a completion.

        Args:
            messages: List of chat messages
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Content chunks as they are generated

        Raises:
            TogetherAPIError: If API request fails
        """
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        logger.debug(
            "llm_stream_request",
            model=model,
            message_count=len(messages),
        )

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(
                        "llm_stream_error",
                        status_code=response.status_code,
                        error=error_text.decode(),
                    )
                    raise TogetherAPIError(response.status_code, error_text.decode())

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    # SSE format: "data: {...}"
                    if line.startswith("data: "):
                        data_str = line[6:]

                        # End of stream
                        if data_str == "[DONE]":
                            break

                        try:
                            import json

                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                yield content

                        except (json.JSONDecodeError, KeyError, IndexError) as e:
                            logger.warning(
                                "llm_stream_parse_error",
                                line=line,
                                error=str(e),
                            )
                            continue

        logger.debug("llm_stream_complete", model=model)

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed(
        self,
        *,
        text: str,
        model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> list[float]:
        """Generate text embedding.

        Args:
            text: Text to embed
            model: Embedding model identifier

        Returns:
            Embedding vector as list of floats

        Raises:
            TogetherAPIError: If API request fails
        """
        # Truncate text if too long (most embedding models have ~8k token limit)
        max_chars = 32000  # Approximate limit
        if len(text) > max_chars:
            text = text[:max_chars]

        payload = {
            "model": model,
            "input": text,
        }

        logger.debug(
            "llm_embed_request",
            model=model,
            text_length=len(text),
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/embeddings",
                headers=self._get_headers(),
                json=payload,
            )

            if response.status_code != 200:
                error_detail = response.text
                logger.error(
                    "llm_embed_error",
                    status_code=response.status_code,
                    error=error_detail,
                )
                raise TogetherAPIError(response.status_code, error_detail)

            data = response.json()

        embedding = data["data"][0]["embedding"]

        logger.debug(
            "llm_embed_success",
            model=model,
            embedding_dim=len(embedding),
        )

        return embedding

    async def embed_batch(
        self,
        *,
        texts: list[str],
        model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            model: Embedding model identifier

        Returns:
            List of embedding vectors
        """
        # Process in batches to avoid API limits
        batch_size = 10
        embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            for text in batch:
                embedding = await self.embed(text=text, model=model)
                embeddings.append(embedding)

        return embeddings
