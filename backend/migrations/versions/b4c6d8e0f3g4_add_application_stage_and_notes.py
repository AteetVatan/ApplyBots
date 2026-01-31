"""Add application stage and notes

Revision ID: b4c6d8e0f3g4
Revises: a3b5c7d9e1f2
Create Date: 2026-01-31 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b4c6d8e0f3g4'
down_revision: Union[str, None] = 'a3b5c7d9e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add stage column to applications and create application_notes table."""
    # Create ApplicationStage enum type
    application_stage_enum = sa.Enum(
        'saved', 'applied', 'interviewing', 'offer', 'rejected',
        name='applicationstage'
    )
    application_stage_enum.create(op.get_bind(), checkfirst=True)

    # Add stage and stage_updated_at columns to applications
    op.add_column(
        'applications',
        sa.Column(
            'stage',
            application_stage_enum,
            nullable=False,
            server_default='saved'
        )
    )
    op.add_column(
        'applications',
        sa.Column('stage_updated_at', sa.DateTime(), nullable=True)
    )

    # Create application_notes table
    op.create_table(
        'application_notes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['application_id'],
            ['applications.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_application_notes_application_id'),
        'application_notes',
        ['application_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove stage column and drop application_notes table."""
    # Drop application_notes table
    op.drop_index(
        op.f('ix_application_notes_application_id'),
        table_name='application_notes'
    )
    op.drop_table('application_notes')

    # Remove columns from applications
    op.drop_column('applications', 'stage_updated_at')
    op.drop_column('applications', 'stage')

    # Drop enum type
    application_stage_enum = sa.Enum(name='applicationstage')
    application_stage_enum.drop(op.get_bind(), checkfirst=True)
