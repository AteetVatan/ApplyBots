"""Add remote work and timing intelligence columns.

Revision ID: f8g0h2i4j6k8
Revises: e7f9g1h3i5j7
Create Date: 2026-01-31 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f8g0h2i4j6k8"
down_revision: str | None = "e7f9g1h3i5j7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create RemoteType enum via raw SQL
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE remotetype AS ENUM (
                'onsite', 'hybrid', 'remote', 'remote_us', 'remote_global'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Reference existing enum type
    remote_type_enum = postgresql.ENUM(
        "onsite",
        "hybrid",
        "remote",
        "remote_us",
        "remote_global",
        name="remotetype",
        create_type=False,
    )

    # Add remote work columns to jobs table
    op.add_column(
        "jobs",
        sa.Column(
            "remote_type",
            remote_type_enum,
            server_default="onsite",
            nullable=False,
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("remote_score", sa.Integer, server_default="0"),
    )
    op.add_column(
        "jobs",
        sa.Column("timezone_requirements", sa.JSON, server_default="[]"),
    )

    # Add timing metadata columns to applications table
    op.add_column(
        "applications",
        sa.Column("applied_day_of_week", sa.Integer, nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("applied_hour", sa.Integer, nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("days_after_posting", sa.Integer, nullable=True),
    )


def downgrade() -> None:
    # Remove columns from applications
    op.drop_column("applications", "days_after_posting")
    op.drop_column("applications", "applied_hour")
    op.drop_column("applications", "applied_day_of_week")

    # Remove columns from jobs
    op.drop_column("jobs", "timezone_requirements")
    op.drop_column("jobs", "remote_score")
    op.drop_column("jobs", "remote_type")

    # Drop RemoteType enum via raw SQL
    op.execute("DROP TYPE IF EXISTS remotetype")
