"""add_min_quantity_and_max_quantity_to_stock_type

Revision ID: 31e43f2db41b
Revises: a4caeb81d1b
Create Date: 2013-12-11 11:09:30.167594

"""

# revision identifiers, used by Alembic.
revision = '31e43f2db41b'
down_revision = 'a4caeb81d1b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('StockType', sa.Column('min_quantity', sa.Integer(), nullable=True))
    op.add_column('StockType', sa.Column('max_quantity', sa.Integer(), nullable=True))
    op.add_column('StockType', sa.Column('min_product_quantity', sa.Integer(), nullable=True))
    op.add_column('StockType', sa.Column('max_product_quantity', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('StockType', 'min_quantity')
    op.drop_column('StockType', 'max_quantity')
    op.drop_column('StockType', 'min_product_quantity')
    op.drop_column('StockType', 'max_product_quantity')

