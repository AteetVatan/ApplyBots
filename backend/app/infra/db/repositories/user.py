"""User repository implementation.

Standards: python_clean.mdc
- Implements Protocol interface
- Async methods
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.user import User, UserRole
from app.infra.db.models import UserModel


class SQLUserRepository:
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        result = await self._session.get(UserModel, user_id)
        return self._to_domain(result) if result else None

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, user: User) -> User:
        """Create a new user."""
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            email_verified=user.email_verified,
            created_at=user.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        """Update an existing user."""
        model = await self._session.get(UserModel, user.id)
        if model:
            model.email = user.email
            model.password_hash = user.password_hash
            model.role = user.role
            model.email_verified = user.email_verified
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"User {user.id} not found")

    async def delete(self, user_id: str) -> None:
        """Delete a user."""
        model = await self._session.get(UserModel, user_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
            email_verified=model.email_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
