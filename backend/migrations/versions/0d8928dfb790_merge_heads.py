"""merge_heads

Revision ID: 0d8928dfb790
Revises: 73121bdb7cc3, g9h1i3j5k7l9
Create Date: 2026-02-06 15:14:40.705214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d8928dfb790'
down_revision: Union[str, None] = ('73121bdb7cc3', 'g9h1i3j5k7l9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
