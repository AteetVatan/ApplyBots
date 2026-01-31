"""User domain model.

Standards: python_clean.mdc
- Enum for constants
- Dataclass for domain models
- No magic numbers
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """User role enumeration."""

    USER = "user"
    ADMIN = "admin"


@dataclass
class User:
    """User domain entity."""

    id: str
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    email_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
