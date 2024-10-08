"""freq_topics

Revision ID: c4f98ebffcfe
Revises: 7e99d35f9081
Create Date: 2024-09-21 06:48:31.279774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4f98ebffcfe'
down_revision: Union[str, None] = '7e99d35f9081'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('threads', sa.Column('frequency', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('threads', 'frequency')
    # ### end Alembic commands ###
