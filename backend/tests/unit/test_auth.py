"""Tests for authentication service.

Standards: python_clean.mdc
- AAA pattern
- Mock external dependencies
"""

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest

from app.core.domain.user import User
from app.core.exceptions import InvalidCredentialsError, ResourceAlreadyExistsError
from app.infra.auth.jwt import create_token, decode_access_token
from app.infra.auth.password import hash_password, verify_password
from app.infra.auth.service import AuthService


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    def test_hash_password_returns_different_hash(self) -> None:
        """Test that hashing produces different output each time (due to salt)."""
        # Arrange
        password = "SecurePass123!"

        # Act
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Assert
        assert hash1 != password
        assert hash2 != password
        assert hash1 != hash2  # Different salts

    def test_verify_password_correct(self) -> None:
        """Test password verification with correct password."""
        # Arrange
        password = "SecurePass123!"
        hashed = hash_password(password)

        # Act
        result = verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_incorrect(self) -> None:
        """Test password verification with incorrect password."""
        # Arrange
        password = "SecurePass123!"
        hashed = hash_password(password)

        # Act
        result = verify_password("WrongPassword", hashed)

        # Assert
        assert result is False


class TestJWTTokens:
    """Tests for JWT token handling."""

    def test_create_access_token(self) -> None:
        """Test access token creation."""
        # Arrange
        user_id = "user-123"
        secret = "test-secret-key"

        # Act
        token = create_token(
            user_id=user_id,
            secret_key=secret,
            algorithm="HS256",
            expires_delta=timedelta(minutes=30),
            token_type="access",
        )

        # Assert
        assert token is not None
        assert len(token) > 0

    def test_decode_access_token(self) -> None:
        """Test access token decoding."""
        # Arrange
        user_id = "user-123"
        secret = "test-secret-key"
        token = create_token(
            user_id=user_id,
            secret_key=secret,
            algorithm="HS256",
            expires_delta=timedelta(minutes=30),
            token_type="access",
        )

        # Act
        payload = decode_access_token(
            token=token,
            secret_key=secret,
            algorithm="HS256",
        )

        # Assert
        assert payload["sub"] == user_id
        assert payload["type"] == "access"


class TestAuthService:
    """Tests for AuthService."""

    @pytest.fixture
    def mock_user_repo(self):
        """Create mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def auth_service(self, mock_user_repo) -> AuthService:
        """Create auth service with mocks."""
        return AuthService(
            user_repository=mock_user_repo,
            secret_key="test-secret",
            algorithm="HS256",
            access_expire_minutes=30,
            refresh_expire_days=7,
        )

    @pytest.mark.asyncio
    async def test_signup_success(
        self,
        auth_service: AuthService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test successful signup."""
        # Arrange
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = User(
            id="new-user-id",
            email="new@example.com",
            password_hash="hashed",
        )

        # Act
        tokens = await auth_service.signup(
            email="new@example.com",
            password="SecurePass123!",
        )

        # Assert
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_signup_existing_email(
        self,
        auth_service: AuthService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test signup with existing email."""
        # Arrange
        mock_user_repo.get_by_email.return_value = User(
            id="existing-user",
            email="existing@example.com",
            password_hash="hashed",
        )

        # Act & Assert
        with pytest.raises(ResourceAlreadyExistsError):
            await auth_service.signup(
                email="existing@example.com",
                password="SecurePass123!",
            )

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        auth_service: AuthService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test successful login."""
        # Arrange
        password = "SecurePass123!"
        mock_user_repo.get_by_email.return_value = User(
            id="user-123",
            email="user@example.com",
            password_hash=hash_password(password),
        )

        # Act
        tokens = await auth_service.login(
            email="user@example.com",
            password=password,
        )

        # Assert
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        auth_service: AuthService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test login with wrong password."""
        # Arrange
        mock_user_repo.get_by_email.return_value = User(
            id="user-123",
            email="user@example.com",
            password_hash=hash_password("CorrectPassword"),
        )

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login(
                email="user@example.com",
                password="WrongPassword",
            )

    @pytest.mark.asyncio
    async def test_login_user_not_found(
        self,
        auth_service: AuthService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test login with non-existent user."""
        # Arrange
        mock_user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login(
                email="nonexistent@example.com",
                password="AnyPassword",
            )
