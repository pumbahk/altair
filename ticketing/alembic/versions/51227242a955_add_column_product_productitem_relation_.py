"""Add Column Product, ProductItem relation lot product

Revision ID: 51227242a955
Revises: 1173311eb7c3
Create Date: 2016-04-18 17:29:44.695436

"""

# revision identifiers, used by Alembic.
revision = '51227242a955'
down_revision = '1604dd750140'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Product', sa.Column('original_product_id', sa.Integer(), nullable=True, default=None))
    op.add_column('ProductItem', sa.Column('original_product_item_id', sa.Integer(), nullable=True, default=None))

def downgrade():
    op.drop_column('Product', 'original_product_id')
    op.drop_column('ProductItem', 'original_product_item_id')
