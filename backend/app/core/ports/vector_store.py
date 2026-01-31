"""Vector store port interface.

Standards: python_clean.mdc
- Protocol for interfaces
- Typed return values
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""

    id: str
    score: float
    metadata: dict[str, str | int | float | bool]


class VectorStore(Protocol):
    """Vector store interface for ChromaDB."""

    async def add_document(
        self,
        *,
        collection: str,
        doc_id: str,
        text: str,
        metadata: dict[str, str | int | float | bool],
    ) -> None:
        """Add a document with auto-generated embedding."""
        ...

    async def add_embedding(
        self,
        *,
        collection: str,
        doc_id: str,
        embedding: list[float],
        metadata: dict[str, str | int | float | bool],
    ) -> None:
        """Add a pre-computed embedding."""
        ...

    async def search(
        self,
        *,
        collection: str,
        query_text: str,
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]:
        """Search by text query."""
        ...

    async def search_by_embedding(
        self,
        *,
        collection: str,
        embedding: list[float],
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]:
        """Search by embedding vector."""
        ...

    async def delete(self, *, collection: str, doc_id: str) -> None:
        """Delete a document from the collection."""
        ...
