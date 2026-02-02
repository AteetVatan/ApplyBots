"""LLM client port interface.

Standards: python_clean.mdc
- Protocol for interfaces
- Async streaming support
"""

from dataclasses import dataclass
from typing import AsyncIterator, Protocol


@dataclass
class LLMMessage:
    """Chat message for LLM."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM response."""

    content: str
    model: str
    usage: dict[str, int]  # prompt_tokens, completion_tokens, total_tokens


class LLMClient(Protocol):
    """LLM client interface for Together AI."""

    async def complete(
        self,
        *,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a completion."""
        ...

    def stream(
        self,
        *,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Stream a completion."""
        ...

    async def embed(
        self,
        *,
        text: str,
        model: str = "BAAI/bge-large-en-v1.5",
    ) -> list[float]:
        """Generate text embedding."""
        ...
