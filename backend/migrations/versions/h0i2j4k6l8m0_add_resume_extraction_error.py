"""Add extraction_error to resumes table

Revision ID: h0i2j4k6l8m0
Revises: 0d8928dfb790
Create Date: 2026-02-06 22:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h0i2j4k6l8m0'
down_revision: Union[str, None] = '0d8928dfb790'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add extraction_error column to resumes table."""
    op.add_column(
        'resumes',
        sa.Column('extraction_error', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Remove extraction_error column from resumes table."""
    op.drop_column('resumes', 'extraction_error')
