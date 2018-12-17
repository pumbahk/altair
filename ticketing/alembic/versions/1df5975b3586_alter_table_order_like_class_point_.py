"""alter table order like class. point_amount

Revision ID: 1df5975b3586
Revises: 3e81e815de52
Create Date: 2018-10-10 17:23:55.170752

"""

# revision identifiers, used by Alembic.
revision = '1df5975b3586'
down_revision = '3e81e815de52'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ProtoOrder', sa.Column('point_amount', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('Cart', sa.Column('point_amount', sa.Numeric(precision=16, scale=2), nullable=False))


def downgrade():
    op.drop_column('ProtoOrder', 'point_amount')
    op.drop_column('Cart', 'point_amount')
