"""Add alerts and gamification tables.

Revision ID: e7f9g1h3i5j7
Revises: d6e8f0g2h4i6
Create Date: 2026-01-31 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7f9g1h3i5j7"
down_revision: str | None = "d6e8f0g2h4i6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create AlertType enum
    alert_type_enum = sa.Enum(
        "dream_job_match",
        "application_status_change",
        "interview_reminder",
        "campaign_milestone",
        "achievement_unlocked",
        "wellness_tip",
        name="alerttype",
    )
    alert_type_enum.create(op.get_bind(), checkfirst=True)

    # Create alerts table
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("alert_type", alert_type_enum, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("data", sa.JSON, server_default="{}"),
        sa.Column("read", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"])
    op.create_index("ix_alerts_read", "alerts", ["read"])
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])

    # Create alert_preferences table
    op.create_table(
        "alert_preferences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("dream_job_threshold", sa.Integer, server_default="90"),
        sa.Column("interview_reminder_hours", sa.Integer, server_default="24"),
        sa.Column("daily_digest", sa.Boolean, server_default="false"),
        sa.Column("enabled_types", sa.JSON, server_default="[]"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # Create user_streaks table
    op.create_table(
        "user_streaks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("current_streak", sa.Integer, server_default="0"),
        sa.Column("longest_streak", sa.Integer, server_default="0"),
        sa.Column("last_activity_date", sa.DateTime, nullable=True),
        sa.Column("total_points", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # Create user_achievements table
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("achievement_id", sa.String(50), nullable=False),
        sa.Column("earned_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_user_achievements_user_id", "user_achievements", ["user_id"])
    op.create_unique_constraint(
        "uq_user_achievement", "user_achievements", ["user_id", "achievement_id"]
    )


def downgrade() -> None:
    op.drop_table("user_achievements")
    op.drop_table("user_streaks")
    op.drop_table("alert_preferences")
    op.drop_table("alerts")

    # Drop AlertType enum
    sa.Enum(name="alerttype").drop(op.get_bind(), checkfirst=True)
