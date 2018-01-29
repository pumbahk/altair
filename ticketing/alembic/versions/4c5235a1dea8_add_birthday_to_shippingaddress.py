"""add birthday to ShippingAddress
Revision ID: 4c5235a1dea8
Revises: 10aef87d8125
Create Date: 2017-11-21 19:02:26.320276
"""

# revision identifiers, used by Alembic.
revision = '4c5235a1dea8'
down_revision = '10aef87d8125'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ShippingAddress', sa.Column('birthday', sa.Date(), nullable=True))

def downgrade():
    op.drop_column('ShippingAddress', 'birthday')