"""Add column Order for Point Allocation

Revision ID: 3e81e815de52
Revises: 51dca1130748
Create Date: 2018-10-09 15:28:54.123925

"""

# revision identifiers, used by Alembic.
revision = '3e81e815de52'
down_revision = '51dca1130748'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order', sa.Column('point_amount', sa.Numeric(precision=16, scale=2), nullable=False))

def downgrade():
    op.drop_column('Order', 'point_amount')
