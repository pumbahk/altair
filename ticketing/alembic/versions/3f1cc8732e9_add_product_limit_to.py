"""add_product_limit_to_sales_segment

Revision ID: 3f1cc8732e9
Revises: 246e00308204
Create Date: 2013-10-24 12:51:54.196421

"""

# revision identifiers, used by Alembic.
revision = '3f1cc8732e9'
down_revision = '246e00308204'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentGroup', sa.Column('product_limit', sa.Integer, default=None))
    op.add_column('SalesSegment', sa.Column('product_limit', sa.Integer, default=None))
    op.add_column('SalesSegment', sa.Column('use_default_product_limit', sa.Boolean))

def downgrade():
    op.drop_column('SalesSegmentGroup', 'product_limit')
    op.drop_column('SalesSegment', 'product_limit')
    op.drop_column('SalesSegment', 'use_default_product_limit')
