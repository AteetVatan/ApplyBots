"""Profile repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.profile import Preferences, Profile
from app.infra.db.models import ProfileModel


class SQLProfileRepository:
    """SQLAlchemy implementation of ProfileRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> Profile | None:
        """Get profile by user ID."""
        stmt = select(ProfileModel).where(ProfileModel.user_id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, profile: Profile) -> Profile:
        """Create a new profile."""
        model = ProfileModel(
            id=profile.id,
            user_id=profile.user_id,
            full_name=profile.full_name,
            headline=profile.headline,
            location=profile.location,
            phone=profile.phone,
            linkedin_url=profile.linkedin_url,
            portfolio_url=profile.portfolio_url,
            preferences=self._preferences_to_dict(profile.preferences),
            created_at=profile.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, profile: Profile) -> Profile:
        """Update an existing profile."""
        model = await self._session.get(ProfileModel, profile.id)
        if model:
            model.full_name = profile.full_name
            model.headline = profile.headline
            model.location = profile.location
            model.phone = profile.phone
            model.linkedin_url = profile.linkedin_url
            model.portfolio_url = profile.portfolio_url
            model.preferences = self._preferences_to_dict(profile.preferences)
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"Profile {profile.id} not found")

    def _to_domain(self, model: ProfileModel) -> Profile:
        """Convert ORM model to domain entity."""
        prefs_dict = model.preferences or {}
        preferences = Preferences(
            target_roles=prefs_dict.get("target_roles", []),
            target_locations=prefs_dict.get("target_locations", []),
            remote_only=prefs_dict.get("remote_only", False),
            salary_min=prefs_dict.get("salary_min"),
            salary_max=prefs_dict.get("salary_max"),
            negative_keywords=prefs_dict.get("negative_keywords", []),
            experience_years=prefs_dict.get("experience_years"),
        )
        return Profile(
            id=model.id,
            user_id=model.user_id,
            full_name=model.full_name,
            headline=model.headline,
            location=model.location,
            phone=model.phone,
            linkedin_url=model.linkedin_url,
            portfolio_url=model.portfolio_url,
            preferences=preferences,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _preferences_to_dict(self, preferences: Preferences) -> dict:
        """Convert Preferences to dict for JSON storage."""
        return {
            "target_roles": preferences.target_roles,
            "target_locations": preferences.target_locations,
            "remote_only": preferences.remote_only,
            "salary_min": preferences.salary_min,
            "salary_max": preferences.salary_max,
            "negative_keywords": preferences.negative_keywords,
            "experience_years": preferences.experience_years,
        }
