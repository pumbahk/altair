"""alter table ShippingAddress add column point

Revision ID: 1d67a6111a7
Revises: 2d39cc727512
Create Date: 2013-10-04 14:46:20.379014

"""

# revision identifiers, used by Alembic.
revision = '1d67a6111a7'
down_revision = '2d39cc727512'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ShippingAddress', sa.Column('point', sa.Unicode(255), nullable=True))

def downgrade():
    op.drop_column('ShippingAddress', 'point')
