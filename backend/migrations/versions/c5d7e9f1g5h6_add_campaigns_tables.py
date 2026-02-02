"""Add campaigns and campaign_jobs tables

Revision ID: c5d7e9f1g5h6
Revises: b4c6d8e0f3g4
Create Date: 2026-01-31 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c5d7e9f1g5h6'
down_revision: Union[str, None] = 'b4c6d8e0f3g4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create campaigns and campaign_jobs tables."""
    # Create CampaignStatus enum type via raw SQL (most reliable)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE campaignstatus AS ENUM (
                'draft', 'active', 'paused', 'completed', 'archived'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Reference existing enum type (create_type=False prevents re-creation)
    campaign_status_enum = postgresql.ENUM(
        'draft', 'active', 'paused', 'completed', 'archived',
        name='campaignstatus',
        create_type=False
    )

    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('resume_id', sa.String(length=36), nullable=False),
        # Search criteria
        sa.Column('target_roles', postgresql.JSON, nullable=False, server_default='[]'),
        sa.Column('target_locations', postgresql.JSON, nullable=False, server_default='[]'),
        sa.Column('target_countries', postgresql.JSON, nullable=False, server_default='[]'),
        sa.Column('target_companies', postgresql.JSON, nullable=False, server_default='[]'),
        sa.Column('remote_only', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('negative_keywords', postgresql.JSON, nullable=False, server_default='[]'),
        # Behavior settings
        sa.Column('auto_apply', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('daily_limit', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('min_match_score', sa.Integer(), nullable=False, server_default='70'),
        sa.Column('send_per_app_email', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cover_letter_template', sa.Text(), nullable=True),
        # Status
        sa.Column('status', campaign_status_enum, nullable=False, server_default='active'),
        # Statistics
        sa.Column('jobs_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_applied', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('interviews', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('offers', sa.Integer(), nullable=False, server_default='0'),
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_campaigns_user_id'),
        'campaigns',
        ['user_id'],
        unique=False
    )

    # Create campaign_jobs table
    op.create_table(
        'campaign_jobs',
        sa.Column('campaign_id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('match_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('adjusted_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default="'pending'"),
        sa.Column('rejection_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        # Constraints
        sa.ForeignKeyConstraint(
            ['campaign_id'],
            ['campaigns.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['job_id'],
            ['jobs.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('campaign_id', 'job_id')
    )
    op.create_index(
        op.f('ix_campaign_jobs_campaign_id'),
        'campaign_jobs',
        ['campaign_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_campaign_jobs_job_id'),
        'campaign_jobs',
        ['job_id'],
        unique=False
    )


def downgrade() -> None:
    """Drop campaigns and campaign_jobs tables."""
    # Drop campaign_jobs table
    op.drop_index(op.f('ix_campaign_jobs_job_id'), table_name='campaign_jobs')
    op.drop_index(op.f('ix_campaign_jobs_campaign_id'), table_name='campaign_jobs')
    op.drop_table('campaign_jobs')

    # Drop campaigns table
    op.drop_index(op.f('ix_campaigns_user_id'), table_name='campaigns')
    op.drop_table('campaigns')

    # Drop enum type via raw SQL
    op.execute("DROP TYPE IF EXISTS campaignstatus")
