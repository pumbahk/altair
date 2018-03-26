"""add the public column to deliverymethod

Revision ID: 267bd8f6b530
Revises: daa86477ebb
Create Date: 2018-03-26 11:01:31.460227

"""

# revision identifiers, used by Alembic.
revision = '267bd8f6b530'
down_revision = 'daa86477ebb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('DeliveryMethod', sa.Column('public', sa.Boolean(), nullable=False, default=True, server_default=text('1')))

def downgrade():
    op.drop_column('DeliveryMethod', 'public')
