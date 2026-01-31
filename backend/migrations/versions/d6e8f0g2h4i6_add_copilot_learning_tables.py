"""Add copilot learning tables and campaign fields

Revision ID: d6e8f0g2h4i6
Revises: c5d7e9f1g5h6
Create Date: 2026-01-31 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd6e8f0g2h4i6'
down_revision: Union[str, None] = 'c5d7e9f1g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add answer_edits table and campaign learning fields."""
    # Create RecommendationMode enum type
    recommendation_mode_enum = sa.Enum(
        'keyword', 'learned',
        name='recommendationmode'
    )
    recommendation_mode_enum.create(op.get_bind(), checkfirst=True)

    # Create answer_edits table for learning from user corrections
    op.create_table(
        'answer_edits',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('question_normalized', sa.String(length=500), nullable=False),
        sa.Column('question_original', sa.Text(), nullable=False),
        sa.Column('original_answer', sa.Text(), nullable=False),
        sa.Column('edited_answer', sa.Text(), nullable=False),
        sa.Column('job_title', sa.String(length=500), nullable=True),
        sa.Column('job_company', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_answer_edits_user_id'),
        'answer_edits',
        ['user_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_answer_edits_question_normalized'),
        'answer_edits',
        ['question_normalized'],
        unique=False
    )

    # Add activated_at column to campaigns table
    op.add_column(
        'campaigns',
        sa.Column('activated_at', sa.DateTime(), nullable=True)
    )

    # Add recommendation_mode column to campaigns table
    op.add_column(
        'campaigns',
        sa.Column(
            'recommendation_mode',
            recommendation_mode_enum,
            nullable=False,
            server_default='keyword'
        )
    )


def downgrade() -> None:
    """Remove answer_edits table and campaign learning fields."""
    # Remove campaign columns
    op.drop_column('campaigns', 'recommendation_mode')
    op.drop_column('campaigns', 'activated_at')

    # Drop answer_edits table
    op.drop_index(op.f('ix_answer_edits_question_normalized'), table_name='answer_edits')
    op.drop_index(op.f('ix_answer_edits_user_id'), table_name='answer_edits')
    op.drop_table('answer_edits')

    # Drop enum type
    recommendation_mode_enum = sa.Enum(name='recommendationmode')
    recommendation_mode_enum.drop(op.get_bind(), checkfirst=True)
