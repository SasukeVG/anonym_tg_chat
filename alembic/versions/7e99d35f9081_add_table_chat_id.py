"""add_table_chat_id

Revision ID: 7e99d35f9081
Revises: d9cbe7abb8fb
Create Date: 2024-09-20 10:14:35.035219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e99d35f9081'
down_revision: Union[str, None] = 'd9cbe7abb8fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('threads', sa.Column('chat_id', sa.BigInteger(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('threads', 'chat_id')
    # ### end Alembic commands ###
