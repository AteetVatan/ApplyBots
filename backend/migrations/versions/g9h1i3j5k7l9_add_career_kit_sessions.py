"""Add career_kit_sessions table.

Revision ID: g9h1i3j5k7l9
Revises: f8g0h2i4j6k8
Create Date: 2026-02-02 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "g9h1i3j5k7l9"
down_revision: str | None = "f8g0h2i4j6k8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create career_kit_sessions table for Expert Apply workflow."""
    # Create CareerKitPhase enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE careerkitphase AS ENUM (
                'analyze', 'questionnaire', 'generate', 'complete'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    career_kit_phase_enum = postgresql.ENUM(
        "analyze",
        "questionnaire",
        "generate",
        "complete",
        name="careerkitphase",
        create_type=False,
    )

    op.create_table(
        "career_kit_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=True),  # NULL for custom JD
        sa.Column("custom_jd", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("session_name", sa.String(length=255), nullable=False),
        sa.Column("is_custom_job", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("phase", career_kit_phase_enum, nullable=False, server_default="analyze"),
        # Resume source
        sa.Column("resume_source_type", sa.String(length=20), nullable=False),  # "uploaded" or "draft"
        sa.Column("resume_source_id", sa.String(length=36), nullable=False),
        # Analysis data
        sa.Column("requirements", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("selected_bullets", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("gap_map", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("questionnaire", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("answers", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        # Generation data
        sa.Column("delta_instructions", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("generated_cv_draft_id", sa.String(length=36), nullable=True),
        sa.Column("interview_prep", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        # Debug/audit
        sa.Column("pipeline_messages", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        # Constraints
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["generated_cv_draft_id"], ["resume_drafts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_career_kit_sessions_user_id"),
        "career_kit_sessions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_career_kit_sessions_job_id"),
        "career_kit_sessions",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop career_kit_sessions table."""
    op.drop_index(op.f("ix_career_kit_sessions_job_id"), table_name="career_kit_sessions")
    op.drop_index(op.f("ix_career_kit_sessions_user_id"), table_name="career_kit_sessions")
    op.drop_table("career_kit_sessions")
    op.execute("DROP TYPE IF EXISTS careerkitphase")
