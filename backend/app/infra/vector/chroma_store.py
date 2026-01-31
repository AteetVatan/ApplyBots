"""ChromaDB vector store implementation.

Standards: python_clean.mdc
- Implements VectorStore protocol
- Async operations where possible
- Proper error handling
"""

from typing import Any

import chromadb
import structlog
from chromadb.config import Settings as ChromaSettings

from app.core.ports.llm import LLMClient
from app.core.ports.vector_store import VectorSearchResult

logger = structlog.get_logger(__name__)

# Collection names
COLLECTION_RESUMES = "resumes"
COLLECTION_JOBS = "jobs"
COLLECTION_AGENT_MEMORY = "agent_memory"
COLLECTION_REJECTED_JOBS_PREFIX = "rejected_jobs_"  # Per-user rejected job patterns


class ChromaVectorStore:
    """ChromaDB implementation of VectorStore protocol.

    Uses Together AI for embedding generation when adding documents by text.
    """

    def __init__(
        self,
        *,
        host: str,
        port: int,
        llm_client: LLMClient | None = None,
    ) -> None:
        """Initialize ChromaDB client.

        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            llm_client: LLM client for generating embeddings (optional)
        """
        self._host = host
        self._port = port
        self._llm = llm_client

        # Initialize client with persistent connection
        self._client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            ),
        )

        # Cache for collections
        self._collections: dict[str, chromadb.Collection] = {}

        logger.info(
            "chroma_store_initialized",
            host=host,
            port=port,
        )

    def _get_collection(self, name: str) -> chromadb.Collection:
        """Get or create a collection.

        Args:
            name: Collection name

        Returns:
            ChromaDB collection
        """
        if name not in self._collections:
            self._collections[name] = self._client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},  # Use cosine similarity
            )
            logger.debug("chroma_collection_created", collection=name)

        return self._collections[name]

    async def add_document(
        self,
        *,
        collection: str,
        doc_id: str,
        text: str,
        metadata: dict[str, str | int | float | bool],
    ) -> None:
        """Add a document with auto-generated embedding.

        Args:
            collection: Collection name
            doc_id: Unique document ID
            text: Document text to embed
            metadata: Document metadata

        Raises:
            ValueError: If LLM client not configured
        """
        if not self._llm:
            raise ValueError("LLM client required for add_document")

        # Generate embedding
        embedding = await self._llm.embed(text=text)

        await self.add_embedding(
            collection=collection,
            doc_id=doc_id,
            embedding=embedding,
            metadata=metadata,
        )

        logger.debug(
            "chroma_document_added",
            collection=collection,
            doc_id=doc_id,
            text_length=len(text),
        )

    async def add_embedding(
        self,
        *,
        collection: str,
        doc_id: str,
        embedding: list[float],
        metadata: dict[str, str | int | float | bool],
    ) -> None:
        """Add a pre-computed embedding.

        Args:
            collection: Collection name
            doc_id: Unique document ID
            embedding: Embedding vector
            metadata: Document metadata
        """
        coll = self._get_collection(collection)

        # Upsert to handle both new and existing documents
        coll.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[self._sanitize_metadata(metadata)],
        )

        logger.debug(
            "chroma_embedding_added",
            collection=collection,
            doc_id=doc_id,
            embedding_dim=len(embedding),
        )

    async def search(
        self,
        *,
        collection: str,
        query_text: str,
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]:
        """Search by text query.

        Args:
            collection: Collection name
            query_text: Text to search for
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of search results sorted by similarity

        Raises:
            ValueError: If LLM client not configured
        """
        if not self._llm:
            raise ValueError("LLM client required for text search")

        # Generate query embedding
        embedding = await self._llm.embed(text=query_text)

        return await self.search_by_embedding(
            collection=collection,
            embedding=embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
        )

    async def search_by_embedding(
        self,
        *,
        collection: str,
        embedding: list[float],
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]:
        """Search by embedding vector.

        Args:
            collection: Collection name
            embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of search results sorted by similarity
        """
        coll = self._get_collection(collection)

        # Build query args
        query_args: dict[str, Any] = {
            "query_embeddings": [embedding],
            "n_results": top_k,
        }

        if filter_metadata:
            query_args["where"] = self._build_where_filter(filter_metadata)

        results = coll.query(**query_args)

        # Parse results
        search_results: list[VectorSearchResult] = []

        if results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            distances = results["distances"][0] if results["distances"] else [0.0] * len(ids)
            metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)

            for doc_id, distance, metadata in zip(ids, distances, metadatas):
                # Convert distance to similarity score (cosine distance -> similarity)
                score = 1.0 - distance

                search_results.append(
                    VectorSearchResult(
                        id=doc_id,
                        score=score,
                        metadata=metadata or {},
                    )
                )

        logger.debug(
            "chroma_search_complete",
            collection=collection,
            top_k=top_k,
            results_count=len(search_results),
        )

        return search_results

    async def delete(self, *, collection: str, doc_id: str) -> None:
        """Delete a document from the collection.

        Args:
            collection: Collection name
            doc_id: Document ID to delete
        """
        coll = self._get_collection(collection)

        try:
            coll.delete(ids=[doc_id])
            logger.debug(
                "chroma_document_deleted",
                collection=collection,
                doc_id=doc_id,
            )
        except Exception as e:
            logger.warning(
                "chroma_delete_failed",
                collection=collection,
                doc_id=doc_id,
                error=str(e),
            )

    async def get_collection_count(self, collection: str) -> int:
        """Get the number of documents in a collection.

        Args:
            collection: Collection name

        Returns:
            Number of documents
        """
        coll = self._get_collection(collection)
        return coll.count()

    async def delete_collection(self, collection: str) -> None:
        """Delete an entire collection.

        Args:
            collection: Collection name
        """
        try:
            self._client.delete_collection(collection)
            self._collections.pop(collection, None)
            logger.info("chroma_collection_deleted", collection=collection)
        except Exception as e:
            logger.warning(
                "chroma_collection_delete_failed",
                collection=collection,
                error=str(e),
            )

    def _sanitize_metadata(
        self, metadata: dict[str, str | int | float | bool]
    ) -> dict[str, str | int | float | bool]:
        """Sanitize metadata for ChromaDB storage.

        ChromaDB only supports str, int, float, bool metadata values.

        Args:
            metadata: Raw metadata

        Returns:
            Sanitized metadata
        """
        sanitized: dict[str, str | int | float | bool] = {}

        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif value is None:
                sanitized[key] = ""
            else:
                sanitized[key] = str(value)

        return sanitized

    def _build_where_filter(
        self, filter_metadata: dict[str, str | int | float | bool]
    ) -> dict[str, Any]:
        """Build ChromaDB where filter.

        Args:
            filter_metadata: Filter conditions

        Returns:
            ChromaDB-compatible where clause
        """
        if len(filter_metadata) == 1:
            key, value = next(iter(filter_metadata.items()))
            return {key: {"$eq": value}}

        # Multiple conditions use $and
        conditions = [{key: {"$eq": value}} for key, value in filter_metadata.items()]
        return {"$and": conditions}
