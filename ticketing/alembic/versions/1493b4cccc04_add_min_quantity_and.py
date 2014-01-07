"""add_min_quantity_and_max_quantity_to_product

Revision ID: 1493b4cccc04
Revises: 46aa7d0c688f
Create Date: 2014-01-04 16:14:07.383665

"""

# revision identifiers, used by Alembic.
revision = '1493b4cccc04'
down_revision = '46aa7d0c688f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Product', sa.Column('min_product_quantity', sa.Integer(), nullable=True))
    op.add_column('Product', sa.Column('max_product_quantity', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('Product', 'min_product_quantity')
    op.drop_column('Product', 'max_product_quantity')

