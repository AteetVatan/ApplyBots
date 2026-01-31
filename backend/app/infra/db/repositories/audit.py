"""Audit log repository implementation."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.models import AuditLogModel


@dataclass
class AuditLog:
    """Audit log domain entity."""

    id: str
    application_id: str
    action: str
    metadata: dict | None
    screenshot_s3_key: str | None
    success: bool
    error_message: str | None
    created_at: datetime


class SQLAuditRepository:
    """SQLAlchemy implementation of AuditRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_application_id(self, application_id: str) -> list[AuditLog]:
        """Get all audit logs for an application."""
        stmt = (
            select(AuditLogModel)
            .where(AuditLogModel.application_id == application_id)
            .order_by(AuditLogModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, audit_log: AuditLog) -> AuditLog:
        """Create a new audit log entry."""
        model = AuditLogModel(
            id=audit_log.id,
            application_id=audit_log.application_id,
            action=audit_log.action,
            action_metadata=audit_log.metadata,
            screenshot_s3_key=audit_log.screenshot_s3_key,
            success=audit_log.success,
            error_message=audit_log.error_message,
            created_at=audit_log.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    def _to_domain(self, model: AuditLogModel) -> AuditLog:
        """Convert ORM model to domain entity."""
        return AuditLog(
            id=model.id,
            application_id=model.application_id,
            action=model.action,
            metadata=model.action_metadata,
            screenshot_s3_key=model.screenshot_s3_key,
            success=model.success,
            error_message=model.error_message,
            created_at=model.created_at,
        )
