"""Add resume_drafts table

Revision ID: a3b5c7d9e1f2
Revises: 8f79a7770571
Create Date: 2026-01-31 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a3b5c7d9e1f2'
down_revision: Union[str, None] = '8f79a7770571'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create resume_drafts table for the resume builder."""
    op.create_table(
        'resume_drafts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('template_id', sa.String(length=50), nullable=False, server_default='professional-modern'),
        sa.Column('ats_score', sa.Integer(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_drafts_user_id'), 'resume_drafts', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop resume_drafts table."""
    op.drop_index(op.f('ix_resume_drafts_user_id'), table_name='resume_drafts')
    op.drop_table('resume_drafts')
