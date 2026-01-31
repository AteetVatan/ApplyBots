"""File storage port interface.

Standards: python_clean.mdc
- Protocol for interfaces
- Async methods with timeouts implied
"""

from typing import Protocol


class FileStorage(Protocol):
    """File storage interface for S3/MinIO."""

    async def upload(
        self,
        *,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file and return the URL."""
        ...

    async def download(self, *, key: str) -> bytes:
        """Download a file by key."""
        ...

    async def delete(self, *, key: str) -> None:
        """Delete a file by key."""
        ...

    async def get_presigned_url(
        self,
        *,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """Get a presigned URL for temporary access."""
        ...

    async def exists(self, *, key: str) -> bool:
        """Check if a file exists."""
        ...
